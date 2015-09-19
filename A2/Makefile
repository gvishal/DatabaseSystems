external-merge-sort: external-merge-sort.cpp
	g++ -Wall -Wextra -pedantic -std=c++0x -O2 \
            -Wshadow -Wformat=2 -Wfloat-equal -Wconversion \
            -Wlogical-op -Wcast-qual -Wcast-align -fwhole-program \
            -D_GLIBCXX_DEBUG -D_GLIBCXX_DEBUG_PEDANTIC -lmcheck \
            -D_FORTIFY_SOURCE=2  -fstack-protector -DDEBUG external-merge-sort.cpp -o external-merge-sort

test: external-merge-sort
	@echo "Running Merge Sort on given file....";
	./external-merge-sort input1.txt actual_output1.txt 1 asc col0

clean:
	-rm external-merge-sort;