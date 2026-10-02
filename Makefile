# include the configuration file
-include config/gryph.mk

# set fallback defaults in case variables are missing
PROFILE ?= ./releng
WORKDIR ?= ./work
OUTDIR  ?= ./output

.PHONY: all packages build clean fast help CheckRoot

# default rule
all: build

# validation rule to ensure mkarchiso runs with sudo/root permissions
check-root:
	@if [ "$$(id -u)" -ne 0 ]; then \
		echo "Error: mkarchiso requires root privileges. Please run with 'sudo make'."; \
		exit 1; \
	fi

# preparation rule to make sure paths exist
prepare:
	@mkdir -p "$(WORKDIR)"
	@mkdir -p "$(OUTDIR)"

packages:
	cd general/gryphd && makepkg -fcs
	cp general/gryphd/*.pkg.tar.zst $(PROFILE)/airootfs/var/lib/gryphon/repo/
	cd $(PROFILE)/airootfs/var/lib/gryphon/repo/ && repo-add -R gryphon.db.tar.zst *.pkg.tar.zst

# main build rule executing mkarchiso
build: check-root prepare
	@echo "Starting mkarchiso build..."
	@echo "Profile:  $(PROFILE)"
	@echo "Work Dir: $(WORKDIR)"
	@echo "Out  Dir: $(OUTDIR)"
	mkarchiso -v -w "$(WORKDIR)" -o "$(OUTDIR)" "$(PROFILE)"

# clean rule 
# NOTE: always verify mountpoints before forcing an rm -rf on workdir!
clean: check-root
	@echo "Cleaning up work directory..."
	@if [ -d "$(WORKDIR)" ]; then \
		findmnt -R "$(WORKDIR)" >/dev/null 2>&1 && { echo "Error: Mount points are active inside $(WORKDIR). Unmount them first."; exit 1; } || true; \
		rm -rf "$(WORKDIR)"; \
	fi
	@echo "Cleaning up output directory..."
	@rm -rf "$(OUTDIR)"

# fast rule
fast: check-root prepare
	@echo "Starting FAST mkarchiso build..."
	@echo "Profile:  $(PROFILE)"
	@echo "Work Dir: $(WORKDIR)"
	@echo "Out  Dir: $(OUTDIR)"
	@sudo rm -f $(WORKDIR)base._make_custom_airootfs \
		$(WORKDIR)base._make_customize_airootfs \
		$(WORKDIR)base._prepare_airootfs_image \
		$(WORKDIR)base._mkairootfs_squashfs \
		$(WORKDIR)build._build_buildmode_iso \
		$(WORKDIR)iso._build_iso_image
	
	mkarchiso -v -w "$(WORKDIR)" -o "$(OUTDIR)" "$(PROFILE)"

help:
	@echo "Usage:"
	@echo "  sudo make          - Build the ISO using parameters from config.mk"
	@echo "  sudo make fast     - Quick build the ISO using parameters from config.mk. Use only if you know what you're doing"
	@echo "  sudo make clean    - Safely wipe the WORKDIR and OUTDIR files"
	@echo "  sudo make build PROFILE=/path/to/profile - Override profile via CLI"
