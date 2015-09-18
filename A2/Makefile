module1: external-merge-sort.cpp
	g++ -Wall -Wextra -pedantic -std=c++0x -O2 \
            -Wshadow -Wformat=2 -Wfloat-equal -Wconversion \
            -Wlogical-op -Wcast-qual -Wcast-align -fwhole-program \
            -D_GLIBCXX_DEBUG -D_GLIBCXX_DEBUG_PEDANTIC -lmcheck \
            -D_FORTIFY_SOURCE=2  -fstack-protector -DDEBUG external-merge-sort.cpp -o module1

test: module1
	@echo "Running Syntax analyser on given program....";
	./module1 input.txt output.txt 1 asc c0 c1

clean:
	-rm module1 1;