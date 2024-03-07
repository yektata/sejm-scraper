import requests
from bs4 import BeautifulSoup
import os

def prime(fileIntegrityOverride=[False,False,False,False],forceHTMLNoChecks=False):
    
    currentdir = os.getcwd()
    rootdir = os.path.join(currentdir,"content")
    HTMLdir = os.path.join(rootdir,"dateHTML")
    voteHTMLdir = os.path.join(rootdir,"votesHTML")
    PDFdir = os.path.join(rootdir,"pdfs")
    homepagePath = os.path.join(rootdir,"homepage.htm")
    baseURL = "https://www.sejm.gov.pl/Sejm9.nsf/"
    homepageURL = "https://www.sejm.gov.pl/Sejm9.nsf/agent.xsp?symbol=posglos&NrKadencji=9"

    polish_months = {
    'stycznia': 1,
    'lutego': 2,
    'marca': 3,
    'kwietnia': 4,
    'maja': 5,
    'czerwca': 6,
    'lipca': 7,
    'sierpnia': 8,
    'wrzeÅ›nia': 9,
    'paÅºdziernika': 10,
    'listopada': 11,
    'grudnia': 12
    }

    os.makedirs(rootdir, exist_ok=True)
    os.makedirs(HTMLdir, exist_ok=True)
    os.makedirs(voteHTMLdir, exist_ok=True)
    os.makedirs(PDFdir, exist_ok=True)

    if (not os.path.exists(homepagePath)) or (fileIntegrityOverride[0]):
        homepageRaw = requests.get(homepageURL)
        if homepageRaw.status_code == 200:
            print(f"got homepage\n")
            with open(homepagePath, 'w', encoding='utf-8') as homepageFile:
                homepageFile.write(homepageRaw.text)
        else:
            print(f"The homepage gave a status code of {homepageRaw.status_code}!\nExpected 200.\nThe link provided is:\n{homepageURL}\n")
            return

    with open(homepagePath, 'r') as homepageFile:
        
        homepageSoup = BeautifulSoup(homepageFile, 'html.parser')
        allDateLinks = homepageSoup.find(name='div', attrs={"id":"title_content"}).find_all('a')
        
        for linkRaw in allDateLinks:
            dateTemp = linkRaw.text.rstrip(" r.").split()
            date = f"{dateTemp[2]}-{polish_months[dateTemp[1]]}-{dateTemp[0]}"
            link = f"{baseURL}{linkRaw.get('href')}"
            if fileIntegrityOverride[1]:
                with open(os.path.join(HTMLdir,"date-links-downloaded.txt"), 'w'):
                    pass
            existing_links = open(os.path.join(HTMLdir,"date-links-downloaded.txt"), 'r').read()
            with open(os.path.join(HTMLdir,"date-links-downloaded.txt"),'a+', encoding='utf-8') as dateLinksTXT:
                if not link in existing_links:
                    pageRaw = requests.get(link)
                    dateLinksTXT.write(f"{link}\n")
                    if pageRaw.status_code == 200:
                        print(f"got link id: {link[link.rfind('='):]}")
                        with open(os.path.join(HTMLdir,f"{date}.htm"), 'w', encoding='utf-8') as pageFile:
                            pageFile.write(pageRaw.text)
                    else:
                        print(f"The page gave a status code of {pageRaw.status_code}!\nExpected 200.\nThe link provided is:\n{link}\nContinuing download process.\n")
                else:
                    print(f"have link id: {link[-4:]}")

        if not forceHTMLNoChecks:
            for subpage in os.listdir(HTMLdir):
                print(subpage)
                if subpage[-3:] != "htm":
                    break
                with open(os.path.join(HTMLdir,subpage), 'r', encoding='utf-8') as subpageFile:
                    subpageSoup = BeautifulSoup(subpageFile, 'html.parser')
                    subpageBody = subpageSoup.find(name='div', attrs={"id":"contentBody"}).find('tbody')
                    for article in subpageBody.find_all("tr"):
                        sublink = article.find("td")
                        sublinkTime = sublink.find_next("td")
                        sublink = f"{baseURL}{sublink.find('a').get('href')}"
                        sublinkTime = sublinkTime.text
                        if fileIntegrityOverride[2] or (not os.path.exists(os.path.join(voteHTMLdir,"vote-links-downloaded.txt"))):
                            with open(os.path.join(voteHTMLdir,"vote-links-downloaded.txt"), 'w'):
                                pass
                        vote_existing_links = open(os.path.join(voteHTMLdir,"vote-links-downloaded.txt"), 'r').read()
                        with open(os.path.join(voteHTMLdir,"vote-links-downloaded.txt"),'a+', encoding='utf-8') as voteLinksTXT:
                            if not sublink in vote_existing_links:
                                votePageRaw = requests.get(sublink)
                                voteLinksTXT.write(f"{sublink}\n")
                                if votePageRaw.status_code == 200:
                                    print(f"got link id: {sublink[sublink.rfind('='):]}")
                                    with open(os.path.join(voteHTMLdir,f"{subpage[:-4]}-{sublinkTime.replace(':','-')}.htm"), 'w', encoding='utf-8') as votePageFile:
                                        votePageFile.write(votePageRaw.text)
                                else:
                                    print(f"The page gave a status code of {votePageRaw.status_code}!\nExpected 200.\nThe link provided is:\n{sublink}\nContinuing download process.\n")
                            else:
                                print(f"have link id: {sublink[-3:]}")

        for pdfpage in os.listdir(voteHTMLdir):
            if pdfpage[-3:] != "htm":
                break
            with open(os.path.join(voteHTMLdir,pdfpage), 'r', encoding='utf-8') as pdfHTML:
                pdfSoup = BeautifulSoup(pdfHTML, 'html.parser')
                pdflink = pdfSoup.find(name='div', attrs={"class":"sub-title"}).find('a').get('href')
                if fileIntegrityOverride[3] or (not os.path.exists(os.path.join(PDFdir,"pdfs-downloaded.txt"))):
                    with open(os.path.join(PDFdir,"pdfs-downloaded.txt"), 'w'):
                        pass
                pdf_existing_links = open(os.path.join(PDFdir,"pdfs-downloaded.txt"), 'r').read()
                with open(os.path.join(PDFdir,"pdfs-downloaded.txt"),'a+', encoding='utf-8') as pdfLinksTXT:
                    if not pdflink in pdf_existing_links:
                        pdfPageRaw = requests.get(pdflink)
                        if pdfPageRaw.status_code == 200:
                            pdfLinksTXT.write(f"{pdflink}\n")
                            print(f"got link id: {pdflink[pdflink.rfind('&'):]}")
                            with open(os.path.join(PDFdir,f"{pdfpage[:-4]}.pdf"), 'wb') as pdfPageFile:
                                pdfPageFile.write(pdfPageRaw.content)
                        else:
                            print(f"The page gave a status code of {pdfPageRaw.status_code}!\nExpected 200.\nThe link provided is:\n{pdflink}\nContinuing download process.\n")
                    else:
                        print(f"have link: {pdflink}")

prime(forceHTMLNoChecks=True)
