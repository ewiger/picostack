#!/bin/bash
cd figaro
MYAPP=$(basename $(dirname `readlink -m settings.py`));DJANGOAPPS=$(echo 'import settings; print " ".join([ str(app).lstrip("'${MYAPP}'.") for app in settings.INSTALLED_APPS if "'${MYAPP}'" in app ])' | python - ); python manage.py sqlreset $DJANGOAPPS | mysql -u root --password ${MYAPP}

