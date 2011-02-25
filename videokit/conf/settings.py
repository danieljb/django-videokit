
import os
from django.conf import settings

# Path in media folder where videos are stored
VIDEO_PATH          = getattr(settings, 'VIDEO_PATH', os.path.join(settings.MEDIA_ROOT, 'videos'));
VIDEO_SEARCH_PATH   = getattr(settings, 'VIDEO_SEARCH_PATH', os.path.join(VIDEO_PATH, 'ftp_uploads'))
VIDEO_PATH_FILTER   = getattr(settings, 'VIDEO_PATH_FILTER', '.+\.flv')
