# Biblioteca de matemáticas financieras en COBOL (GnuCOBOL, formato libre).
SHELL := /bin/bash
.SHELLFLAGS := -eu -o pipefail -c

COBC     := bash scripts/cobc-strict.sh
COBFLAGS := -free -Wall -I copybooks
export COB_CFLAGS := -O2 -pipe -fsigned-char -Wno-unused

BUILD   := build
LIBPATH := $(CURDIR)/$(BUILD)

MODULES := fin-potencia fin-interes fin-anualidad fin-prestamo \
           fin-vpn-tir fin-depreciacion
MAINS   := fin-calc fin-lote demo-interes demo-prestamo demo-tir \
           demo-anualidad demo-depreciacion

MODULE_SOS := $(addprefix $(BUILD)/,$(addsuffix .so,$(MODULES)))
MAIN_BINS  := $(addprefix $(BUILD)/,$(MAINS))

.PHONY: all modules programs test demo clean

all: modules programs

modules: $(MODULE_SOS)

programs: $(MAIN_BINS) $(BUILD)/fin-humo

$(BUILD):
	mkdir -p $(BUILD)

$(BUILD)/%.so: src/%.cbl | $(BUILD)
	$(COBC) -m $(COBFLAGS) -o $@ $<

$(BUILD)/fin-calc: src/fin-calc.cbl | $(BUILD)
	$(COBC) -x $(COBFLAGS) -o $@ $<

$(BUILD)/fin-lote: src/fin-lote.cbl | $(BUILD)
	$(COBC) -x $(COBFLAGS) -o $@ $<

$(BUILD)/demo-interes: src/demo-interes.cbl | $(BUILD)
	$(COBC) -x $(COBFLAGS) -o $@ $<

$(BUILD)/demo-prestamo: src/demo-prestamo.cbl | $(BUILD)
	$(COBC) -x $(COBFLAGS) -o $@ $<

$(BUILD)/demo-tir: src/demo-tir.cbl | $(BUILD)
	$(COBC) -x $(COBFLAGS) -o $@ $<

$(BUILD)/demo-anualidad: src/demo-anualidad.cbl | $(BUILD)
	$(COBC) -x $(COBFLAGS) -o $@ $<

$(BUILD)/demo-depreciacion: src/demo-depreciacion.cbl | $(BUILD)
	$(COBC) -x $(COBFLAGS) -o $@ $<

$(BUILD)/fin-humo: tests/fin-humo.cbl | $(BUILD)
	$(COBC) -x $(COBFLAGS) -o $@ $<

test: all
	COB_LIBRARY_PATH=$(LIBPATH) $(BUILD)/fin-humo
	COB_LIBRARY_PATH=$(LIBPATH) python3 -m unittest -v tests/test_finanzas.py
	$(MAKE) demo

demo: all
	mkdir -p ejemplos
	COB_LIBRARY_PATH=$(LIBPATH) $(BUILD)/demo-interes | tee ejemplos/demo-interes.txt
	COB_LIBRARY_PATH=$(LIBPATH) $(BUILD)/demo-prestamo | tee ejemplos/demo-prestamo.txt
	COB_LIBRARY_PATH=$(LIBPATH) $(BUILD)/demo-tir | tee ejemplos/demo-tir.txt
	COB_LIBRARY_PATH=$(LIBPATH) $(BUILD)/demo-anualidad | tee ejemplos/demo-anualidad.txt
	COB_LIBRARY_PATH=$(LIBPATH) $(BUILD)/demo-depreciacion | tee ejemplos/demo-depreciacion.txt
	COB_LIBRARY_PATH=$(LIBPATH) $(BUILD)/fin-calc samples/ordenes.txt | tee ejemplos/fin-calc.txt
	COB_LIBRARY_PATH=$(LIBPATH) $(BUILD)/fin-lote samples/lote.dat ejemplos/informe.txt ejemplos/informe.csv

clean:
	rm -rf $(BUILD)
