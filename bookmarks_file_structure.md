# Structure and Format of Firefox and Chrome HTML/JSON bookmark file exports.

## 1) Firefox HTML Bookmarks file structure

All the Firefox bookmarks in an HTML file are contained inside the main `<DL><p>` list.

All the `<H3>` and `<A>` items in the main list that don't contain special attributes set to `true` are items that are located inside the `Bookmarks Menu` folder.

The special folders `Bookmarks Toolbar` and `Other Bookmarks` in the main list, have a special attribute to indicate their type. The `Mobile Bookmarks` folder is not included in the HTML file when being exported (Firefox does not export `Mobile Bookmarks` to an HTML file), you need to export the bookmarks as JSON or use the firefox sqlite database file backup to export your `Mobile Bookmarks`.

#### Firefox HTML Bookmark file Template

```html
[Netscape Bookmark File Headers]
<H1>Bookmarks Menu</H1> <!-- Different "H1" Content than Chrome -->

<DL><p>
    <!-- The <H3> and <A> tags inside the main <DL><p> are inside the "Bookmarks Menu" folder. -->
    <DT><H3></H3>
    <DT><A></A>
    <!-- Folder containing the Personal_Toolbar_Folder attribute set to true is the "Bookmarks Toolbar"
    folder -->
    <DT><H3 PERSONAL_TOOLBAR_FOLDER="true"></H3>
    <DL><p>
        <!-- Contents of "Bookmarks Toolbar" -->
        <DT><H3></H3>
        <DT><A></A>
    </DL><p>
    <!-- Folder containing the Unified_Bookmarks_Folder attribute set to true is the "Other Bookmarks"
    folder -->
    <DT><H3 UNFILED_BOOKMARKS_FOLDER="true"></H3>
    <DL><p>
        <!-- Contents of "Other Bookmarks" -->
        <DT><H3></H3>
        <DT><A></A>
    </DL><p>
</DL><p>
```
#### Firefox HTML Folder template
```html
<DT><H3 ADD_DATE="1599750431" LAST_MODIFIED="1599750431">Mozilla Firefox</H3>
```
the folder can also contain an addition attribute that states the *special* role of the folder:
- `PERSONAL_TOOLBAR_FOLDER="true"`: for the `Toolbar` folder.
- `UNFILED_BOOKMARKS_FOLDER="true"`: for the `Other Bookmarks` folder.

#### Firefox HTML URL template
```html
<DT><A HREF="https://www.mozilla.org/en-US/contribute/" ADD_DATE="1599750431" LAST_MODIFIED="1599750431" ICON_URI="fake-favicon-uri:https://www.mozilla.org/en-US/contribute/" ICON="data:image/png;base64,PHN2ZyB4bWxucz0naHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmcnIHdpZHRoPScxNicgaGVpZ2h0PScxNic+IDxwYXRoIGQ9J00wIDBoMTZ2MTZIMHonLz4gPHBhdGggZD0nTTEzLjk5NCAxMC4zNTZIMTVWMTJoLTMuMTcxVjcuNzQxYzAtMS4zMDgtLjQzNS0xLjgxLTEuMjktMS44MS0xLjA0IDAtMS40Ni43MzctMS40NiAxLjh2Mi42M2gxLjAwNlYxMkg2LjkxOFY3Ljc0MWMwLTEuMzA4LS40MzUtMS44MS0xLjI5MS0xLjgxLTEuMDM5IDAtMS40NTkuNzM3LTEuNDU5IDEuOHYyLjYzaDEuNDQxVjEySDF2LTEuNjQ0aDEuMDA2VjYuMDc5SDFWNC40MzVoMy4xNjh2MS4xMzlhMi41MDcgMi41MDcgMCAwIDEgMi4zLTEuMjlBMi40NTIgMi40NTIgMCAwIDEgOC45MzEgNS45MSAyLjUzNSAyLjUzNSAwIDAgMSAxMS40IDQuMjg0IDIuNDQ4IDIuNDQ4IDAgMCAxIDE0IDYuOXYzLjQ1OHonIGZpbGw9JyNmZmYnLz4gPC9zdmc+">Get Involved</A>
```
The two attributes `ICON_URI` and `ICON` are optional and sometimes not included.

---

## 2) Chrome HTML Bookmarks file structure

Just like in Firefox, all the Chrome bookmarks in an HTML file are contained inside the main `<DL><p>` list.

The main list usually starts with the `Bookmarks bar` folder, all the bookmarks that follow the `Bookmarks bar`'s `<H3>` and are located inside the main list are either inside the `Other Bookmarks` or `Mobile Bookmarks` folder. Unlike the Firefox HTML file, the `Mobile Bookmarks` folder is included inside the HTML export, but they are included right after the `Other Bookmarks` `<H3>` and `<A>` items without any kind of separator, so it is not possible to differentiate between them (the `Other bookmarks` and `Mobile Bookmarks`) from within the HTML file.

#### Chrome HTML Bookmark file Template

```html
[Netscape Bookmark File Headers]
<H1>Bookmarks</H1> <!-- Different H1 Content than Firefox -->
<DL><p>
    <!-- Folder containing the Personal_Toolbar_Folder attribute set to true is the "Bookmarks bar"
     folder -->
    <DT><H3 PERSONAL_TOOLBAR_FOLDER="true"></H3>
    <DL><p>
        <!-- Contents of "Bookmarks bar" -->
        <DT><H3></H3>
        <DT><A></A>
    </DL><p>
    <!-- All the "H3" and "A" tags that come after the "Bookmarks bar" "H3" folder,
     and are in the main list, are links and folder from inside the "Other Bookmarks" folder -->
    <DT><H3></H3>
    <DL><p>
        <DT><H3></H3>
        <DT><A></A>
    </DL><p>
    <DT><A></A>
    <!-- Chrome appends the "Mobile Bookmarks" folder items (<H3> and <A>) after the "Other Bookmarks"
        folder items, there is no separator or identifier so it is not possible to identify them from
        the HTML file -->
    <DT><H3></H3>
    <DL><p>
        <DT><H3></H3>
        <DT><A></A>
    </DL><p>
    <DT><A></A>
</DL><p>
```
#### Chrome HTML Folder template
```html
<DT><H3 ADD_DATE="1599759836" LAST_MODIFIED="0">Social</H3>
```
the folder can also contain an addition attribute that states the *special* role of the folder:
- `PERSONAL_TOOLBAR_FOLDER="true"`: for the `Bookmarks bar` folder.

#### Chrome HTML URL template
```html
<DT><A HREF="https://www.mozilla.org/en-US/contribute/" ADD_DATE="1599750431" ICON="data:image/png;base64,PHN2ZyB4bWxucz0naHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmcnIHdpZHRoPScxNicgaGVpZ2h0PScxNic+IDxwYXRoIGQ9J00wIDBoMTZ2MTZIMHonLz4gPHBhdGggZD0nTTEzLjk5NCAxMC4zNTZIMTVWMTJoLTMuMTcxVjcuNzQxYzAtMS4zMDgtLjQzNS0xLjgxLTEuMjktMS44MS0xLjA0IDAtMS40Ni43MzctMS40NiAxLjh2Mi42M2gxLjAwNlYxMkg2LjkxOFY3Ljc0MWMwLTEuMzA4LS40MzUtMS44MS0xLjI5MS0xLjgxLTEuMDM5IDAtMS40NTkuNzM3LTEuNDU5IDEuOHYyLjYzaDEuNDQxVjEySDF2LTEuNjQ0aDEuMDA2VjYuMDc5SDFWNC40MzVoMy4xNjh2MS4xMzlhMi41MDcgMi41MDcgMCAwIDEgMi4zLTEuMjlBMi40NTIgMi40NTIgMCAwIDEgOC45MzEgNS45MSAyLjUzNSAyLjUzNSAwIDAgMSAxMS40IDQuMjg0IDIuNDQ4IDIuNDQ4IDAgMCAxIDE0IDYuOXYzLjQ1OHonIGZpbGw9JyNmZmYnLz4gPC9zdmc+">Get Involved</A>
```
The `ICON` attribute is optional and sometimes not included.

---

## 3) Firefox JSON Bookmarks file structure

Firefox allows users to export the bookmarks as a JSON file.
The `.json` file has a root folder, which has the following folders as children:

- `menu` : which is the "Bookmarks Menu" folder.
- `toolbar` : which is the "Bookmarks Toolbar" folder.
- `unfiled` : which is the "Other Bookmarks" folder.
- `mobile` : which is the "Mobile Bookmarks" folder.

1. #### Json folder Template

```json
{
  "guid": "K3LUb7o0kSUt",
  "title": "Main Folder",
  "index": 0,
  "dateAdded": 1599750431776000,
  "lastModified": 1599750431776000,
  "id": 1,
  "typeCode": 2,
  "type": "text/x-moz-place-container",
  "children": []
}
```

2. #### Json url Template

```json
{
  "guid": "7TpRGhofxKDv",
  "title": "Google",
  "index": 0,
  "dateAdded": 1599750431776000,
  "lastModified": 1599750431776000,
  "id": 2,
  "typeCode": 1,
  "iconuri": None,
  "type": "text/x-moz-place",
  "uri": "https://www.google.com"
}
```

---

## 4) Chrome JSON Bookmarks file structure

Chrome doesn't allow you to export or backup your bookmarks as a .json file, but you can get a copy of the .json file chrome stores your bookmarks in. Depending on your OS and browser (chrome/chromium), these are the locations of the file:

- `Linux [Chrome]` --> `~/.config/google-chrome`
- `Linux [Chromium]` --> `~/.config/chromium`
- `Mac OS X [Chrome]` --> `~/Library/Application Support/Google/Chrome`
- `Mac OS X [Chromium]` --> `~/Library/Application Support/Chromium`
- `Windows [Chrome]` --> `%LOCALAPPDATA%\Google\Chrome\User Data`
- `Windows [Chromium]` --> `%LOCALAPPDATA%\Chromium\User Data`

**NOTE:** Chrome's timestamps start from a different epoch than the Unix epoch (chrome counts in microseconds from `1601-01-01T00:00:00Z`). You can convert the chrome epoch to Unix epoch by the following equation:

```
Unix Epoch = Chrome Epoch - 11644473600000000
```

1. #### Json folder Template

```json
{
  "children": [],
  "date_added": "13244233436520764",
  "date_modified": "0",
  "id": "1",
  "name": "Main Folder",
  "type": "folder"
}
```

2. #### Json url Template

```json
{
  "date_added": "13244224395000000",
  "id": "2",
  "name": "Google",
  "type": "url",
  "url": "https://www.google.com"
}
```

---

## 5) Custom Json exported by this BookmarksConverter

If you export your bookmarks as a .json file using this BookmarksConverter package, you will get a json format that will look as follows:

1. #### Json folder Template

```json
{
  "type": "folder",
  "id": 1,
  "index": 0,
  "title": "Main Folder",
  "date_added": 0,
  "children": []
}
```

2. ### Json url Template

```json
{
  "type": "url",
  "id": 2,
  "index": 0,
  "url": "https://www.google.com",
  "title": "Google",
  "date_added": 0,
  "icon": None,
  "iconuri": None,
  "tags": None
}
```
