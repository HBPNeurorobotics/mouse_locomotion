OUT_DIR?=dist
BLENDER_REMOTE_REP=http://download.blender.org/release/
BLENDER_VERS=Blender2.77
BLENDER_FILE=blender-2.77-linux-glibc211-x86_64

install_blender:
	if [ ! -d $(OUT_DIR)/${BLENDER_VERS} ]; then \
		mkdir -p $(OUT_DIR); \
		wget "${BLENDER_REMOTE_REP}${BLENDER_VERS}/${BLENDER_FILE}.tar.bz2"; \
		tar -xvf "${BLENDER_FILE}.tar.bz2"; \
		mv ${BLENDER_FILE} $(OUT_DIR)/${BLENDER_VERS}; \
		rm "${BLENDER_FILE}.tar.bz2"; \
	fi
