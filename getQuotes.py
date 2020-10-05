import nuggetsv2

quotes = nuggetsv2.getQuotesByAuthor("Shakespeare", 175,3)
for quote in quotes:
    print(quote[0])