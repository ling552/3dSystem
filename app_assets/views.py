import mimetypes
import os
import zipfile
from pathlib import Path

from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import AvatarForm, ProfileForm, RegisterForm, UploadAssetForm
from .models import ModelAsset


def _is_safe_zip_member(name: str) -> bool:
    try:
        p = Path(name)
    except Exception:
        return False
    if p.is_absolute():
        return False
    parts = p.parts
    if not parts:
        return False
    if any(part in ('..',) for part in parts):
        return False
    return True


def _extract_zip_to_dir(uploaded_file, dest_dir: Path) -> list[Path]:
    dest_dir.mkdir(parents=True, exist_ok=True)
    extracted: list[Path] = []
    with zipfile.ZipFile(uploaded_file) as zf:
        for info in zf.infolist():
            name = info.filename
            if not name or name.endswith('/'):
                continue
            if not _is_safe_zip_member(name):
                continue

            out_path = (dest_dir / name).resolve()
            if dest_dir.resolve() not in out_path.parents and out_path != dest_dir.resolve():
                continue

            out_path.parent.mkdir(parents=True, exist_ok=True)
            with zf.open(info, 'r') as src, open(out_path, 'wb') as dst:
                while True:
                    chunk = src.read(1024 * 1024)
                    if not chunk:
                        break
                    dst.write(chunk)
            extracted.append(out_path)
    return extracted


def home(request):
    if request.user.is_authenticated:
        return redirect('asset_list')
    return redirect('login')


def register(request):
    if request.user.is_authenticated:
        return redirect('asset_list')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('asset_list')
    else:
        form = RegisterForm()

    return render(request, 'registration/register.html', {'form': form})


@login_required
def profile(request):
    _ = getattr(request.user, 'profile', None)
    return render(request, 'app_assets/profile.html')


@login_required
def profile_edit(request):
    profile = getattr(request.user, 'profile', None)
    if profile is None:
        from .models import UserProfile

        profile = UserProfile.objects.create(user=request.user)
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=request.user)
        avatar_form = AvatarForm(request.POST, request.FILES, instance=profile)
        if form.is_valid() and avatar_form.is_valid():
            form.save()
            avatar_form.save()
            return redirect('profile')
    else:
        form = ProfileForm(instance=request.user)
        avatar_form = AvatarForm(instance=profile)
    return render(request, 'app_assets/profile_edit.html', {'form': form, 'avatar_form': avatar_form})


@login_required
def upload_asset(request):
    if request.method == 'POST':
        form = UploadAssetForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded = form.cleaned_data['file']
            ext = os.path.splitext(uploaded.name)[1].lower()
            asset = ModelAsset(
                owner=request.user,
                name=form.cleaned_data['name'],
                visibility=form.cleaned_data['visibility'],
                original_filename=uploaded.name,
                size_bytes=getattr(uploaded, 'size', 0) or 0,
                status=ModelAsset.Status.UPLOADED,
            )
            asset.save()

            if ext == '.zip':
                dest_dir = Path(settings.MEDIA_ROOT) / 'models' / str(request.user.id) / str(asset.id)
                extracted_files = _extract_zip_to_dir(uploaded, dest_dir)

                gltfs = [p for p in extracted_files if p.suffix.lower() == '.gltf']
                glbs = [p for p in extracted_files if p.suffix.lower() == '.glb']
                main = (gltfs[0] if gltfs else (glbs[0] if glbs else None))
                if not main:
                    asset.deleted_at = timezone.now()
                    asset.save(update_fields=['deleted_at'])
                    form.add_error('file', '压缩包中未找到 .gltf 或 .glb 主模型文件')
                    return render(request, 'app_assets/upload.html', {'form': form})

                rel_name = main.relative_to(Path(settings.MEDIA_ROOT)).as_posix()
                asset.file.name = rel_name
                asset.original_filename = main.name
                asset.save(update_fields=['file', 'original_filename'])
            else:
                asset.file.save(uploaded.name, uploaded, save=True)

            asset.status = ModelAsset.Status.READY
            asset.save(update_fields=['status'])
            return redirect('viewer', asset_id=asset.id)
    else:
        form = UploadAssetForm()

    return render(request, 'app_assets/upload.html', {'form': form})


@login_required
def asset_list(request):
    q = (request.GET.get('q') or '').strip()
    sort = (request.GET.get('sort') or 'new').strip()

    assets = ModelAsset.objects.filter(owner=request.user, deleted_at__isnull=True)

    if q:
        assets = assets.filter(Q(name__icontains=q) | Q(original_filename__icontains=q))

    if sort == 'old':
        assets = assets.order_by('created_at')
    else:
        assets = assets.order_by('-created_at')

    paginator = Paginator(assets, 10)
    page = paginator.get_page(request.GET.get('page') or 1)

    return render(
        request,
        'app_assets/asset_list.html',
        {
            'page': page,
            'q': q,
            'sort': sort,
            'public_mode': False,
        },
    )


@login_required
def asset_public_list(request):
    q = (request.GET.get('q') or '').strip()
    sort = (request.GET.get('sort') or 'new').strip()

    assets = ModelAsset.objects.filter(visibility=ModelAsset.Visibility.PUBLIC, deleted_at__isnull=True)

    if q:
        assets = assets.filter(Q(name__icontains=q) | Q(original_filename__icontains=q) | Q(owner__username__icontains=q))

    if sort == 'old':
        assets = assets.order_by('created_at')
    else:
        assets = assets.order_by('-created_at')

    paginator = Paginator(assets, 10)
    page = paginator.get_page(request.GET.get('page') or 1)

    return render(
        request,
        'app_assets/asset_list.html',
        {
            'page': page,
            'q': q,
            'sort': sort,
            'public_mode': True,
        },
    )


@login_required
def asset_detail(request, asset_id):
    asset = get_object_or_404(ModelAsset, id=asset_id, deleted_at__isnull=True)
    if asset.owner_id != request.user.id and asset.visibility != ModelAsset.Visibility.PUBLIC:
        raise Http404()
    return render(request, 'app_assets/asset_detail.html', {'asset': asset})


@login_required
def viewer(request, asset_id):
    asset = get_object_or_404(ModelAsset, id=asset_id, deleted_at__isnull=True)
    if asset.owner_id != request.user.id and asset.visibility != ModelAsset.Visibility.PUBLIC:
        raise Http404()

    model_url = asset.file.url
    return render(request, 'app_assets/viewer.html', {'asset': asset, 'model_url': model_url})


@login_required
def asset_delete(request, asset_id):
    asset = get_object_or_404(ModelAsset, id=asset_id, owner=request.user, deleted_at__isnull=True)
    if request.method == 'POST':
        asset.deleted_at = timezone.now()
        asset.save(update_fields=['deleted_at'])
        return redirect('asset_list')
    return render(request, 'app_assets/asset_delete.html', {'asset': asset})


@login_required
def asset_download(request, asset_id):
    asset = get_object_or_404(ModelAsset, id=asset_id, deleted_at__isnull=True)
    if asset.owner_id != request.user.id and asset.visibility != ModelAsset.Visibility.PUBLIC:
        raise Http404()

    if not asset.file:
        raise Http404()

    file_path = asset.file.path
    if not os.path.exists(file_path):
        raise Http404()

    content_type, _ = mimetypes.guess_type(file_path)
    resp = FileResponse(open(file_path, 'rb'), content_type=content_type or 'application/octet-stream')
    resp['Content-Length'] = str(asset.size_bytes or 0)
    resp['Content-Disposition'] = f'attachment; filename="{asset.original_filename}"'
    return resp
