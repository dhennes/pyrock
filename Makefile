ifndef AUTOPROJ_CURRENT_ROOT
$(error AUTOPROJ_CURRENT_ROOT is not set)
endif

BUILD_DIR := pyrock/build

ROOT_DIR:=$(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))
ROCK_INCLUDE_DIR := $(AUTOPROJ_CURRENT_ROOT)/install/include
IDL_DIR := $(ROOT_DIR)/idl

all: copy_rtt copy_messages omniorbpy

copy_rtt: $(IDL_DIR)
	cd $(ROCK_INCLUDE_DIR)/rtt && \
	find . -name \*.idl -exec cp {} $(IDL_DIR) \;

copy_messages: $(IDL_DIR)
	cd $(ROCK_INCLUDE_DIR)/orocos && \
	find . -name \*.idl -exec cp --parents {} $(IDL_DIR) \;

omniorbpy: $(BUILD_DIR)
	cd $(BUILD_DIR) && \
	find $(IDL_DIR) -name \*.idl -exec omniidl -v -I$(IDL_DIR) -bpython {} \;

$(IDL_DIR):
	mkdir -p $(IDL_DIR)

$(BUILD_DIR):
	mkdir -p $(BUILD_DIR)

clean:
	rm -rf $(IDL_DIR)
	rm -rf $(BUILD_DIR)
