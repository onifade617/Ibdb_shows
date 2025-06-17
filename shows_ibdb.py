from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from time import sleep
from urllib.parse import urljoin
import re
import pandas as pd
from urllib.parse import urlparse
import os



scraped_results_current = []
scraped_results_upcoming = []
tab_urls = []
scraped_results_tours_c = []
scraped_results_tours_u = []

def scrape_ibdb_shows():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                         "AppleWebKit/537.36 (KHTML, like Gecko) "
                         "Chrome/123.0.0.0 Safari/537.36")
    
    # Initialize driver once
    driver = webdriver.Chrome(options=options)
    try:
        url = "https://www.ibdb.com/shows"
        driver.get(url)
        sleep(5)

        soup = BeautifulSoup(driver.page_source, "html.parser")

        tabs = soup.find("div", class_="page-wrapper xtrr")\
            .find("div", class_="shows-page")\
            .find("div", class_="row bgcolor-greyWhite2")\
            .find("div", class_="tabs-wrap")\
            .find("div", class_="xt-c-box")\
            .find("ul", class_="tabs")\
            .find_all("li", class_="tab")

        
        for tab in tabs:
            anchor = tab.find('a')
            href = anchor.get("href")
            if href:
                full_url = urljoin(url, href)
                tab_urls.append(full_url)

        print("Collected tab URLs:")
        for tab_url in tab_urls:
            print(tab_url)       

    finally:
        driver.quit()  # Ensure browser closes even if there's an error







def current_parse():
    
    # Initialize driver once
    driver = webdriver.Chrome()
        
    # === Open the target webpage ===
    driver.get(tab_urls[0])
    sleep(5)  # Allow time for JavaScript to load the content

    # === Get the HTML content and parse it with BeautifulSoup ===
    soup = BeautifulSoup(driver.page_source, "html.parser")
    base_url = "https://www.ibdb.com"

    # === Navigate to the container holding all show cards ===
    heading = soup.find("div", class_="page-wrapper xtrr")\
        .find("div", class_="shows-page")\
        .find("div", class_="row bgcolor-greyWhite2")\
        .find("div", class_="xt-c-box row")\
        .find("div", id="current")\
        .find("div", class_="row show-images xt-iblocks")\
        .find_all("div", class_="xt-iblock")
        # === Loop through each show card to extract individual show links ===
    for link in heading:
        link_indv = link.find("div", class_="xt-iblock-inner")\
            .find("a", href=True)
        img_indv = link_indv.find('span', class_='iblock-image')#image link text
        title = link_indv.find('i').get_text(strip=True)#Title text
        print(title)  

        style = img_indv.get('style', '')

                # Extract URL using regex
        match = re.search(r'url\((.*?)\)', style)
        if match:
            url = match.group(1)
            print(url)
        else:
            print("No URL found")

        if link_indv:
            full_url = base_url + link_indv['href']#production detals link
            print(full_url)
                
            
            for attempt in range(3):  # Maximum of 3 attempts
                driver.set_page_load_timeout(300) 
                try:
                    driver.get(full_url)
                    sleep(5)
                    break  # Break out of loop if successful
                except Exception as e:
                    print(f"[Attempt {attempt+1}] Error loading {full_url}: {e}")
                    if attempt == 1:  # On second failure
                        print(f"Skipping {full_url} after two failed attempts.")
                        continue  # Move to the next show

            
                
                # === Parse the individual show page ===
            show_soup = BeautifulSoup(driver.page_source, "html.parser")
            base_bar1 = show_soup.find("body", class_="winOS")
                #print(show_soup.prettify())  # (Optional) print full HTML structure

                
           
                    # === Drill down to show detail section ===
            base_bar = base_bar1.find("div", class_=re.compile("^production-page"))\
                    .find("div", class_=re.compile("^xt-c-box"))\
                    .find("div", class_="row xt-fixed-sidebar-row")

                    # === Navigate to image/title/type container ===
            img_type_title = base_bar.find("div", class_=re.compile("col l4 m10 push-m1 s12 s12 xt-l-col-left"))\
                    .find("div", class_=re.compile("production-info-panel"))\
                    .find("div", class_=re.compile("xt-fixed-sidebar"))\
                    .find("div", class_= re.compile("xt-fixed-block"),attrs={"data-id": "part-b"})
            
            #print(img_type_title.prettify())
            '''
            # === Extract Performance Info (e.g., Broadway, Off-Broadway) ===
            perform = img_type_title.find("div", class_="xt-info-block")\
                .find_all("div", class_="row wrapper")
            
            try:
                third_instance = perform[1].find(class_='col s7 m6 l7 txt-paddings vertical-divider')\
                    .find("div", class_="xt-main-title").text
            except:
                third_instance =  None  
            
            print(third_instance)
            '''

             # === Extract Show Type (e.g. Musical, Play) ===
            show_type_origin = img_type_title.find("div", class_="row wrapper hide-on-small-and-down")\
                .find("div")\
                .find_all("i")
            
            #Extract Show Type 
            show_type = show_type_origin[0].text
            print(show_type)

            #Extract Show origin 
            show_origin = show_type_origin[1].text
            print(show_origin)

            #First Production
            Age_of_First_prod = img_type_title.find("div", class_="xt-info-block")\
                .find("div", class_="row wrapper hide-on-med-only")\
                .find("div", class_="col s12 txt-paddings")\
                .find("div", class_="xt-main-title").text.strip()
            
            print(Age_of_First_prod)
        


            '''
            # === Locate the venue and date section ===
            venue_date_parent = base_bar.find("div", class_=re.compile("col l8 m12 def-text s12 xt-l-col-right"))\
                .find_all("div", class_="row")

            # Try to find the div with id='venues' (fallback from index 1 to 2)
            venue_container = venue_date_parent[1]
            venues_div = venue_container.find(id="venues")
            if not venues_div:
                venue_container = venue_date_parent[2]
                venues_div = venue_container.find(id="venues")

            if not venues_div:
                raise Exception("Missing div with id='venues' in both venue_date_parent[1] and [2]")

            # === Extract Theatre Name and Opening Date ===
            theatre_div = venues_div.find("div", class_=re.compile("col s12 m4 theatre"))
            if not theatre_div:
                raise Exception("Missing theatre div")

            row_blocks = theatre_div.find_all("div", class_="row")
            if len(row_blocks) < 2:
                raise Exception("Unexpected number of row divs in theatre block")

            venue = row_blocks[1].find("a").text.strip()
            date = row_blocks[1].find("i").text.strip()
            '''

            status = "Active"
            market = "USA"

            scraped_results_current.append({
                "Title": title,
                "Production type" : show_type,
                "Status" : status,
                "Origin" : show_origin,
                "Market presence" : market,
                "Age of production" : Age_of_First_prod,
                "Web page Link" : full_url,
                "Image Link" : url

            })



    driver.quit()



def saved_file():
    # File path
    file_path = "scraped_shows.csv"

   

    # Create DataFrames
    new_df = pd.DataFrame(scraped_results_current)
    new_df2 = pd.DataFrame(scraped_results_upcoming)
    new_df3 = pd.DataFrame(scraped_results_tours_c)
    new_df4 = pd.DataFrame(scraped_results_tours_u)

    # Combine both and drop exact duplicates
    submit_df = pd.concat([new_df, new_df2, new_df3, new_df4], ignore_index=True).drop_duplicates(subset=["Title", "Status", "Age of production"])

    if os.path.exists(file_path):
        # Load existing data
        existing_df = pd.read_csv(file_path)

        # Concatenate with new data and drop duplicates
        combined_df = pd.concat([existing_df, submit_df], ignore_index=True).drop_duplicates(subset=["Title", "Status", "Age of production"])

        # Save back to CSV
        combined_df.to_csv(file_path, index=False)
    else:
        # Save new data as new CSV
        submit_df.to_csv(file_path, index=False)









def upcoming_parse():
    
    driver = webdriver.Chrome()
    
        
    # === Open the target webpage ===
    driver.get(tab_urls[1])
    sleep(5)  # Allow time for JavaScript to load the content

    # === Get the HTML content and parse it with BeautifulSoup ===
    soup = BeautifulSoup(driver.page_source, "html.parser")
    base_url = "https://www.ibdb.com"

    # === Navigate to the container holding all show cards ===
    heading = soup.find("div", class_="page-wrapper xtrr")\
        .find("div", class_="shows-page")\
        .find("div", class_="row bgcolor-greyWhite2")\
        .find("div", class_="xt-c-box row")\
        .find("div", id="upcoming")\
        .find("div", class_="row show-images xt-iblocks")\
        .find_all("div", class_="xt-iblock")
        # === Loop through each show card to extract individual show links ===
    for link in heading:
        link_indv = link.find("div", class_="xt-iblock-inner")\
            .find("a", href=True)
        img_indv = link_indv.find('span', class_='iblock-image')#image link text
        title = link_indv.find('i').get_text(strip=True)#Title text
        print(title)  

        style = img_indv.get('style', '')

                # Extract URL using regex
        match = re.search(r'url\((.*?)\)', style)
        if match:
            url = base_url + match.group(1)
            print(url)
        else:
            print("No URL found")

        if link_indv:
            full_url = base_url + link_indv['href']#production detals link
            print(full_url)

            for attempt in range(2): # Maximum of 3 attempts
                driver.set_page_load_timeout(300) 
                try:
                    driver.get(full_url)
                    sleep(5)
                    break  # Break out of loop if successful
                except Exception as e:
                    print(f"[Attempt {attempt+1}] Error loading {full_url}: {e}")
                    if attempt == 1:  # On second failure
                        print(f"Skipping {full_url} after two failed attempts.")
                        continue  # Move to the next show

            
                
                # === Parse the individual show page ===
            show_soup = BeautifulSoup(driver.page_source, "html.parser")
            base_bar1 = show_soup.find("body", class_="winOS")
                #print(show_soup.prettify())  # (Optional) print full HTML structure

                
           
                    # === Drill down to show detail section ===
            base_bar = base_bar1.find("div", class_=re.compile("^production-page"))\
                    .find("div", class_=re.compile("^xt-c-box"))\
                    .find("div", class_="row xt-fixed-sidebar-row")

                    # === Navigate to image/title/type container ===
            img_type_title = base_bar.find("div", class_=re.compile("col l4 m10 push-m1 s12 s12 xt-l-col-left"))\
                    .find("div", class_=re.compile("production-info-panel"))\
                    .find("div", class_=re.compile("xt-fixed-sidebar"))\
                    .find("div", class_= re.compile("xt-fixed-block"),attrs={"data-id": "part-b"})
            
            #print(img_type_title.prettify())
            # === Extract Performance Info (e.g., Broadway, Off-Broadway) ===
            perform = img_type_title.find("div", class_="xt-info-block")\
                .find_all("div", class_="row wrapper")
            
            try:
                third_instance = perform[1].find(class_='col s7 m6 l7 txt-paddings vertical-divider')\
                    .find("div", class_="xt-main-title").text
            except:
                third_instance =  None  
            
            print(third_instance)

             # === Extract Show Type (e.g. Musical, Play) ===
            show_type_origin = img_type_title.find("div", class_="row wrapper hide-on-small-and-down")\
                .find("div")\
                .find_all("i")
            
            #Extract Show Type 
            show_type = show_type_origin[0].text
            print(show_type)

            #Extract Show origin 
            show_origin = show_type_origin[1].text
            print(show_origin)

            #First Production
            try:
                
                Age_of_First_prod = img_type_title.find("div", class_="xt-info-block")\
                    .find("div", class_="row wrapper hide-on-med-only")\
                    .find("div", class_="col s12 txt-paddings")\
                    .find("div", class_="xt-main-title").text.strip()
            except AttributeError:
                try:
                    # Fallback: Check an alternate node
                    Age_of_First_prod = img_type_title.find("div", class_="xt-info-block")\
                        .find("div", class_="row wrapper")\
                        .find("div", class_="col s5 m3 15 txt-paddings")\
                        .find("div", class_="xt-main-title").text.strip()
                except AttributeError:
                    Age_of_First_prod = None

            
            print(Age_of_First_prod)


            status = "Upcoming"
            market = "USA"

            scraped_results_upcoming.append({
                "Title": title,
                "Production type" : show_type,
                "Status" : status,
                "Origin" : show_origin,
                "Market presence" : market,
                "Age of production" : Age_of_First_prod,
                "Web page Link" : full_url,
                "Image Link" : url

            })





    driver.quit()





def current_tours_parse():
    
    # Initialize driver once
    driver = webdriver.Chrome()
    
        
    # === Open the target webpage ===
    driver.get(tab_urls[2])
    sleep(5)  # Allow time for JavaScript to load the content

    # === Get the HTML content and parse it with BeautifulSoup ===
    soup = BeautifulSoup(driver.page_source, "html.parser")
    base_url = "https://www.ibdb.com"

    # === Navigate to the container holding all show cards ===
    heading = soup.find("div", class_="page-wrapper xtrr")\
        .find("div", class_="shows-page")\
        .find("div", class_="row bgcolor-greyWhite2")\
        .find("div", class_="xt-c-box row")\
        .find("div", id="current-tours")\
        .find("div", class_="row show-images xt-iblocks")\
        .find_all("div", class_="xt-iblock")
        # === Loop through each show card to extract individual show links ===
    for link in heading:
        link_indv = link.find("div", class_="xt-iblock-inner")\
            .find("a", href=True)
        img_indv = link_indv.find('span', class_='iblock-image')#image link text
        title = link_indv.find('i').get_text(strip=True)#Title text
        print(title)  

        style = img_indv.get('style', '')

                # Extract URL using regex
        match = re.search(r'url\((.*?)\)', style)
        if match:
            url =  base_url + match.group(1)
            print(url)
        else:
            print("No URL found")

        if link_indv:
            full_url = base_url + link_indv['href']#production detals link
            print(full_url)

            for attempt in range(3):  # Maximum of 3 attempts
                driver.set_page_load_timeout(300) 
                try:
                    driver.get(full_url)
                    sleep(5)
                    break  # Break out of loop if successful
                except Exception as e:
                    print(f"[Attempt {attempt+1}] Error loading {full_url}: {e}")
                    if attempt == 1:  # On second failure
                        print(f"Skipping {full_url} after two failed attempts.")
                        continue  # Move to the next show

            
                
                # === Parse the individual show page ===
            show_soup = BeautifulSoup(driver.page_source, "html.parser")
            base_bar1 = show_soup.find("body", class_="winOS")
                #print(show_soup.prettify())  # (Optional) print full HTML structure

                
           
                    # === Drill down to show detail section ===
            base_bar = base_bar1.find("div", class_=re.compile("^production-page"))\
                    .find("div", class_=re.compile("^xt-c-box"))\
                    .find("div", class_="row xt-fixed-sidebar-row")

                    # === Navigate to image/title/type container ===
            img_type_title = base_bar.find("div", class_=re.compile("col l4 m10 push-m1 s12 s12 xt-l-col-left"))\
                    .find("div", class_=re.compile("production-info-panel"))\
                    .find("div", class_=re.compile("xt-fixed-sidebar"))\
                    .find("div", class_= re.compile("xt-fixed-block"),attrs={"data-id": "part-b"})
            
            #print(img_type_title.prettify())
            

             # === Extract Show Type (e.g. Musical, Play) ===
            show_type_origin = img_type_title.find_all("div", class_="row wrapper")
        
            
            #Extract Show Type 
            show_type_prod = show_type_origin[1].find("div", class_= 'col s12 txt-paddings tag-block-compact')\
                .find_all("i")
            show_type = show_type_prod[0].text
            print(show_type)

            #Extract Show origin 
            show_origin_prod = show_type_origin[1].find("div", class_= 'col s12 txt-paddings tag-block-compact')\
                .find_all("i")
            show_origin = show_origin_prod[2].text
            print(show_origin)

            #First Production
            Age_of_First_prod = show_type_origin[0].find("div", class_= 'col s6 txt-paddings')\
                .find("h4").text
            
            print(Age_of_First_prod)
        


            status = "Active"
            market = "USA"

            scraped_results_tours_c.append({
                "Title": title,
                "Production type" : show_type,
                "Status" : status,
                "Origin" : show_origin,
                "Market presence" : market,
                "Age of production" : Age_of_First_prod,
                "Web page Link" : full_url,
                "Image Link" : url

            })









    driver.quit()




def upcoming_tours_parse():
    
    driver = webdriver.Chrome()
    
        
    # === Open the target webpage ===
    driver.get(tab_urls[3])
    sleep(5)  # Allow time for JavaScript to load the content

    # === Get the HTML content and parse it with BeautifulSoup ===
    soup = BeautifulSoup(driver.page_source, "html.parser")
    base_url = "https://www.ibdb.com"

    # === Navigate to the container holding all show cards ===
    heading = soup.find("div", class_="page-wrapper xtrr")\
        .find("div", class_="shows-page")\
        .find("div", class_="row bgcolor-greyWhite2")\
        .find("div", class_="xt-c-box row")\
        .find("div", id="upcoming-tours")\
        .find("div", class_="row show-images xt-iblocks")\
        .find_all("div", class_="xt-iblock")
        # === Loop through each show card to extract individual show links ===
    for link in heading:
        link_indv = link.find("div", class_="xt-iblock-inner")\
            .find("a", href=True)
        img_indv = link_indv.find('span', class_='iblock-image')#image link text
        title = link_indv.find('i').get_text(strip=True)#Title text
        print(title)  

        style = img_indv.get('style', '')

                # Extract URL using regex
        match = re.search(r'url\((.*?)\)', style)
        if match:
            url = base_url + match.group(1)
            print(url)
        else:
            print("No URL found")

        if link_indv:
            full_url = base_url + link_indv['href']#production detals link
            print(full_url)

            

            for attempt in range(3):  # Maximum of 3 attempts
                driver.set_page_load_timeout(300) 
                try:
                    driver.get(full_url)
                    sleep(5)
                    break  # Break out of loop if successful
                except Exception as e:
                    print(f"[Attempt {attempt+1}] Error loading {full_url}: {e}")
                    if attempt == 1:  # On second failure
                        print(f"Skipping {full_url} after two failed attempts.")
                        continue  # Move to the next show

            
                
                # === Parse the individual show page ===
            show_soup = BeautifulSoup(driver.page_source, "html.parser")
            base_bar1 = show_soup.find("body", class_="winOS")
                #print(show_soup.prettify())  # (Optional) print full HTML structure

                
           
                    # === Drill down to show detail section ===
            base_bar = base_bar1.find("div", class_=re.compile("^production-page"))\
                    .find("div", class_=re.compile("^xt-c-box"))\
                    .find("div", class_="row xt-fixed-sidebar-row")

                    # === Navigate to image/title/type container ===
            img_type_title = base_bar.find("div", class_=re.compile("col l4 m10 push-m1 s12 s12 xt-l-col-left"))\
                    .find("div", class_=re.compile("production-info-panel"))\
                    .find("div", class_=re.compile("xt-fixed-sidebar"))\
                    .find("div", class_= re.compile("xt-fixed-block"),attrs={"data-id": "part-b"})
            
            #print(img_type_title.prettify())
            

             # === Extract Show Type (e.g. Musical, Play) ===
            show_type_origin = img_type_title.find_all("div", class_="row wrapper")
        
            
            #Extract Show Type 
            show_type_prod = show_type_origin[1].find("div", class_= 'col s12 txt-paddings tag-block-compact')\
                .find_all("i")
            show_type = show_type_prod[0].text
            print(show_type)

            #Extract Show origin 
            show_origin_prod = show_type_origin[1].find("div", class_= 'col s12 txt-paddings tag-block-compact')\
                .find_all("i")
            show_origin = show_origin_prod[2].text
            print(show_origin)

            #First Production
            Age_of_First_prod = show_type_origin[0].find("div", class_= 'col s6 txt-paddings')\
                .find("h4").text
            
            print(Age_of_First_prod)
        


            status = "Upcoming"
            market = "USA"

            scraped_results_tours_u.append({
                "Title": title,
                "Production type" : show_type,
                "Status" : status,
                "Origin" : show_origin,
                "Market presence" : market,
                "Age of production" : Age_of_First_prod,
                "Web page Link" : full_url,
                "Image Link" : url

            })



    driver.quit()


if __name__ == "__main__":
    scrape_ibdb_shows()
    current_parse()
    upcoming_parse()
    current_tours_parse()
    upcoming_tours_parse()
    saved_file()
    
    