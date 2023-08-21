# Release notes
All notable changes to this project will be documented in this file.

## 0.6.0 WIP
- FIX: skip zero now only skips when sum of DEC/MERIT/SPS == 0, not >0
- Migrate data: add opponent to battle log 
- Add card overview page, including clickable from main page.
- Update/Extend Nemesis page


## 0.5.0
- FIX: Break update portfolio when hive market is down
- Separate DEC rental payments in cost and earning
  - NOTE best to remove all season_* files and re-capture all seasonal information
- Add Modern/Wild filter to main page
- Separate overall quantity and value in portfolio tab
- Add Edition and SPS overview in portfolio

## 0.4.0
- Remove previous migrations
- Migrate battle data, add modern or wild format and re-add Zyriel secondary color.
- Use Dash clipboard functionality iso pyperclip, remove pyperclip dependency
- Update git repository link in hive blog to the new tool
- Add daily battle graph 
- Make portfolio graph clickable to give detail overview of categories 

## 0.3.1
- Fix bug with tournaments (wrong time validation) 

## 0.3.0
- Fix crash when no battles are played for a day
- Separated market_purchases in buy_market_purchases and sell_market_purchases
  - Necessary to reload all seasonal data this can be done by delete all csv files that start with season_ 
  - restart application
  - Update season information again
- Add generate hive blog
- Add option to use environment variables STORE and DEBUG 
  - Store is create a separate store e.g. one for main account one for alt account
  - Debug is used to switch between development and production more easily without code modification


## 0.2.0
- Migrate data + add rarity of cards to battle stores 
- Add filter and sort options to home page
- Add top 5 cards to home page sorted
- Complete table now behind accordion on the home page
- Update on how land price is calculated when not a perfect match is found take closed match 

## 0.1.0
 - Initial release