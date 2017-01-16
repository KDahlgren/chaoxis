all: deps

deps: get-submodules c4 z3

clean:
	rm -r lib/c4/build
	rm -r lib/z3/build

c4: lib/c4/build/src/libc4/libc4.dylib

z3: lib/z3/build/z3-dist

lib/z3/build/z3-dist: lib/z3/build/libz3.dylib
	# We need to make these parent directories so that Z3's Makefile
	# doesn't complain about them missing when it copies files during
	# the `install` step:
	mkdir -p lib/z3/build/z3-dist/lib/python2.7/dist-packages
	mkdir -p lib/z3/build/z3-dist/lib/python2.6/dist-packages
	cd lib/z3/build && make install

lib/z3/build/libz3.dylib:
	cd lib/z3 && python scripts/mk_make.py --prefix=z3-dist
	cd lib/z3/build && make -j4

lib/c4/build/src/libc4/libc4.dylib:
	@which cmake > /dev/null
	cd lib/c4 && mkdir -p build
	cd lib/c4/build && cmake ..
	(cd lib/c4/build && make ; echo ">>> C4 Installation SUCCESSFUL <<<" ;) 2>&1 | tee c4_out.txt;

get-submodules:
	git submodule init
	git submodule update

CMAKE-installed:

# SBT command for running only the fast unit tests and excluding the slower
# end-to-end tests (which have been tagged using ScalaTest's `Slow` tag):
fast-test: deps
	sbt "testOnly *Suite -- -l org.scalatest.tags.Slow"
