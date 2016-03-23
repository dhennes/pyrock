ifndef AUTOPROJ_CURRENT_ROOT
$(error AUTOPROJ_CURRENT_ROOT is not set)
endif

PACKAGE := pyrock._gen
BUILD_DIR := pyrock/_gen

ROOT_DIR:=$(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))
ROCK_INCLUDE_DIR := $(AUTOPROJ_CURRENT_ROOT)/install/include
IDL_DIR := $(ROOT_DIR)/idl

.PHONY: all test clean

all: copy_rtt copy_messages omniorbpy

copy_rtt: $(IDL_DIR)
	cd $(ROCK_INCLUDE_DIR)/rtt && \
	find . -name \*.idl -exec cp {} $(IDL_DIR) \;

copy_messages: $(IDL_DIR)
	cd $(ROCK_INCLUDE_DIR)/orocos && \
	find . -name \*.idl -exec cp --parents {} $(IDL_DIR) \;

omniorbpy: $(BUILD_DIR)
	omniidl -v -I$(IDL_DIR) -bpython -Wbpackage=$(PACKAGE) `find $(IDL_DIR) -name \*.idl`

$(IDL_DIR):
	mkdir -p $(IDL_DIR)

$(BUILD_DIR):
	mkdir -p $(BUILD_DIR)

test:
	PYTHONPATH=$(ROOT_DIR):${PYTHONPATH} python test/test_pyrock.py

clean:
	rm -rf $(IDL_DIR)
	rm -rf $(BUILD_DIR)
