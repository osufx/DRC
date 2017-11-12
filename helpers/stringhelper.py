import re

def Replace(needle, replace, stack, *, pad_left = 0, pad_right = 0, wrap = False, flags=0):
	r = re.compile(needle, flags=flags)

	if wrap:
		stack = " {} ".format(stack)

	s = r.search(stack)
	while s is not None:
		stack = stack[:s.start() + pad_left] + replace + stack[s.end() - pad_right:]
		s = r.search(stack)

	if wrap:
		stack = stack[1:len(stack)-1]

	return stack