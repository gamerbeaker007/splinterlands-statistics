# Release notes

All notable changes to this project will be documented in this file.

## 0.14.0

- Update filters to new icons add match type filter.
- Make buttons switch theme
- Add Possibility to add token information for battle API

## 0.13.0

- FIX: portfolio staked DEC and SPS where counted double remove from Others category
- FIX: since (season) filter was not determined correctly at startup
- Update: nemesis page update, reversed order of the home team units so lineup matches.

## 0.12.2

- FIX: hive blog generation, sometimes given callback error, error might still appear in console but generation is
  completed

## 0.12.1

- FIX: double legend in rating page

## 0.12.0

- FIX: Add list of un-trade-able items on hive engine so no accidental value can be applied, GOLD potion had value on
  hive engine for a while
- FIX: Add price calculation for CREDITS these are not on hive engine
- Main page: Add small padding on cards, especially for rebellion cards
- Card page: Add graph that shows battles per mana cap
- Make filters re-usable, home/losing pages
- Losing page: Make filterable and show top 5 losing card. Keep complete table in accordion.
- Add Trace option when this option is enable it will log some timing information of all callbacks
- Update libraries to latest versions. Including templates, graphs visually update due to this change.

## 0.11.1

- FIX: portfolio graph error when no investments are done

## 0.11.0

- FIX: Sell cards crash
- Update load portfolio improve load time
- First land implementation
- Add last investment marker for visual effect.

## 0.10.0

- Add monitor of staked DEC
- Update ordering of portfolio ALL graph

## 0.9.3

- FIX portfolio value calculation after land update
- small preparation for rebellion

## 0.9.2

- FIX readonly mode more strict portfolio and config page.
- FIX hive-engine exceptions try also on backup url (switched primary url and secondary url)

## 0.9.1

- FIX sorting of rating table with multiple accounts

## 0.9.0

- FIX: price calculations for tokens was missing REBELLION due to 1000 token limit, include stronger retry mechanism
- Remove previous migrations
- Group by levels is now default on True
- Add since season date on rating page (default last 2 seasons)

## 0.8.0

- FIX: When splinterlands is in maintenance mode skip update, causing application crashes
- Update readme for executable + change linux to ubuntu in github workflow
- Change server mode wait time. After processing daily and season reschedule next pull cycle to 30 minutes.
- Add season pull information to server mode. Including some feedback when rewards are not claimed yet.
- Update page title and remove the "Updating..."

## 0.7.0

- FIX: Home page default from date filter causing error when not loaded fully.
- FIX: Deposit/withdraw exception without account
- FIX: Update season end dates also when season update button is pressed. Was only done on startup not good with server
  mode
- FIX: When a specific card is viewed that is no longer in you possession it did not generate the level correctly
- Change use commandline arguments iso environment variables
- Add read-only mode, unable to change accounts and deposit/withdraw investments
- Add server mode, this will update battle/collection every 90 minutes, portfolio update daily
- Add version info for released versions
- Update add account, now updated directly (no wait for 90 minutes in server mode)
- Update github workflows

## 0.6.0

- FIX: skip zero now only skips when sum of DEC/MERIT/SPS == 0, not >0
- Migrate data: add opponent to battle log
- Migrate data: add Brawl as match type to battle log
- Migrate data: fix opponent for draw battles
- Remove recording of battle (battle.csv), keep battle_big more detailed information
- Add card overview page, including clickable from main page.
- Update/Extend Nemesis page
- Add group level option to main page
- Change hive blog intro image

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