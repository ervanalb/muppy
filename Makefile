CC:=gcc

PYTHON:=python3.8
PY_INC:=-I/usr/include/$(PYTHON)
PY_LD:=-l$(PYTHON)

INC:=$(PY_INC)
LIBS:=$(PY_LD)
CFLAGS:=-shared -fPIC -Werror -Wextra -g $(INC)

COMPONENTS = mupen64plus-input-python

OBJ = $(patsubst %,muppy/%.so,$(COMPONENTS))

muppy/%.so: src/%.c src/plugin_common.c
	$(CC) -o $@ $< $(CFLAGS) $(LIBS)

all: $(OBJ)

.PHONY: clean

clean:
	rm -f mupen64plus/*.so
