install_virtualenv:
	cd static_data && bower install || true
	rm -fr .virtualenv || true
	virtualenv .virtualenv/p2
	chmod +x .virtualenv/p2/bin/activate
	ln -s .virtualenv/p2/bin/activate ap2 || true
	bash ./pip_pkg_install.sh

run_tests:
	bash -c "source ap2; python2 ./runtests.py"
