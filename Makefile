# Batch resize without GUI
# ex:
# IN_DIR=./orig OUT_DIR=./out SCALE=25 make -j$(nproc)
#
IN_DIR ?= ./in_dir
OUT_DIR ?= ./out_dir
SCALE ?= 50
WILCARD ?= *.JPG
SRC_IMAGES = $(wildcard $(IN_DIR)/$(WILCARD))
SMALL_IMAGES = $(patsubst $(IN_DIR)/%,$(OUT_DIR)/small_%, $(SRC_IMAGES))

all: $(SMALL_IMAGES)

$(OUT_DIR)/small_%: $(IN_DIR)/%
	@mkdir -p $(dir $@)
	convert $< -scale $(SCALE)% $@

clean:
	rm $(OUT_DIR)/small_*
