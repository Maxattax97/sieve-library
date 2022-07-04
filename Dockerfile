FROM archlinux:latest

RUN pacman -Syu --noconfirm \
	check-sieve \
	pigeonhole
