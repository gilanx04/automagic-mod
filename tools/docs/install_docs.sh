#!/data/data/com.termux/files/home/automagic/work/docs/install_docs.sh
# Memasang dokumentasi offline Automagic ke data aplikasi (butuh root).
set -e

PKG=ch.gridvision.ppam.androidautomagic
SRC="$(cd "$(dirname "$0")" && pwd)/help-out"
DEST="/data/data/$PKG/files"

if [ ! -d "$SRC/en" ]; then
    echo "dokumentasi belum dibangun; jalankan: python3 work/docs/build_help.py" >&2
    exit 1
fi

UID_APP=$(su -c "stat -c %u /data/data/$PKG" 2>/dev/null || echo "")
GID_APP=$(su -c "stat -c %g /data/data/$PKG" 2>/dev/null || echo "")

su -c "rm -rf $DEST/help $DEST/catalog; mkdir -p $DEST/help $DEST/catalog"
su -c "cp -r '$SRC/en' '$SRC/de' $DEST/help/"
su -c "cp -r '$SRC/catalog/en' '$SRC/catalog/de' $DEST/catalog/"
if [ -n "$UID_APP" ] && [ -n "$GID_APP" ]; then
    su -c "chown -R $UID_APP:$GID_APP $DEST/help $DEST/catalog"
fi

echo "terpasang: $DEST/help (en, de) dan $DEST/catalog (en, de)"
echo "halaman help : $(su -c "ls $DEST/help/en/*.html | wc -l")"
echo "versi offline: $(su -c "cat $DEST/help/en/version.txt")"
