import requests
from bs4 import BeautifulSoup, NavigableString
import math
import Levenshtein
from langdetect import detect

def findAuthorID(author):
    try:
        author = author.replace(" ", "+")
        page = requests.get("https://www.goodreads.com/search?utf8=%E2%9C%93&q=" + author + "&search_type=books&search%5Bfield%5D=author")
        soup = BeautifulSoup(page.text, 'html.parser')
        idLink = soup.find(class_="authorName",href=True)["href"]
        start = idLink.find("show/")
        end = idLink.find("?from")
        authorID = idLink[start+5:end]

        #experimental: trying to find out if the authorID is correct
        nameStart = authorID.find(".")
        authorName = authorID[nameStart+1:].replace("_"," ")
        lDistance = Levenshtein.distance(author,authorName)
        differenceScore = lDistance-len(authorName)+len(author) #bigger is worse

    except:
        print("failed to find author")
        pass
    print("found " + author +" @ " + authorID)
    print("(experimental) difference score = " + str(differenceScore))
    return authorID

def getQuotesByAuthor(author, maxChars, page_num = None):
    all_quotes = []
    authorID = findAuthorID(author)

    if page_num is None:
        try:
            page = requests.get("https://www.goodreads.com/author/quotes/" + authorID)
            soup = BeautifulSoup(page.text, 'html.parser')
            pages = soup.find(class_="smallText").text
            of = pages.find("of ")
            showing = pages.find("Showing ")
            num_shown = pages[showing+10:of-1]
            total_num = pages[of+3:]
            total_num = total_num.replace(",", "").replace("\n", "")
            num_shown = int(num_shown)
            total_num = int(total_num)
            page_num = math.ceil(total_num/num_shown)
            print("looking through", page_num, "pages")

        except:
            page_num = 1


    for i in range(1, page_num+1, 1):
        try:
            page = requests.get("https://www.goodreads.com/author/quotes/" + authorID + "?page=" + str(i))
            soup = BeautifulSoup(page.text, 'html.parser')
            print("scraping page", i, " of ", page_num)
        except:
            print("could not connect to goodreads")
            break    

        try:
            quote = soup.find(class_="quotes")
            quote_list = quote.find_all(class_="quoteDetails")
        except:
            pass

        for quote in quote_list:
            meta_data = []
        # Get quote's text
            try:
                outer = quote.find(class_="quoteText")
                inner_text = [element for element in outer if isinstance(element, NavigableString)]
                final_quote = "\n".join(inner_text[:])
                final_quote = final_quote.replace("\n", " ")
                final_quote = final_quote.replace("―", "").strip()
            except:
                pass 
            if(len(final_quote) < maxChars and len(final_quote) != 0 and detect(final_quote) == "en"):
                    meta_data.append(final_quote)
            else:
                meta_data.append(None)
                continue
            #get quote's tags
            try: 
                title = quote.find(class_="authorOrTitle")
                title = title.nextSibling.nextSibling.text
                title = title.replace("\n", "")
                meta_data.append(title.strip())
            except:
                meta_data.append(None)

            # Get quote's tags
            try:
                tags = quote.find(class_="greyText smallText left").text
                tags = [x.strip() for x in tags.split(',')]
                tags = tags[1:]
                meta_data.append(tags)
            except:
                meta_data.append(None)
            
            # Get number of likes
            try:
                likes = quote.find(class_="right").text
                likes = likes.replace("likes", "")
                likes = int(likes)
                meta_data.append(likes)
            except:
                meta_data.append(None)

            all_quotes.append(meta_data)
    
    return all_quotes
