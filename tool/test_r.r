p1 = HS_RequestParam ('key1', 'Title', 'text')
p2 = HS_RequestParam ('key2', 'X Axis', 'text')
plot (c (1, 2, 3), c (1, 2, 3), xlab = p2)
title (p1)