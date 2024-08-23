# Structure and Format of supported bookmarks files from different browsers.

This file contains all the information gathered about Chrome/Chromium and Firefox while creating BookmarksConverter.

## 1. Chrome / Chromium

The source code that contains all the bookmarks logic can found in the chromium source code:
- [chrome/utility/importer](https://source.chromium.org/chromium/chromium/src/+/main:chrome/utility/importer/)
- [chrome/browser/bookmarks](https://source.chromium.org/chromium/chromium/src/+/main:chrome/browser/bookmarks/)

### a. HTML
All the Chrome bookmarks in an HTML file are contained inside the main `<DL><p>` list.

The main list usually starts with the `Bookmarks bar` folder.
All the bookmarks that follow the `Bookmarks bar`'s `<H3>` and are located inside the main list are either inside the `Other Bookmarks` or `Mobile Bookmarks` folder. 
The `Mobile Bookmarks` folder is included inside the HTML export, but they are included right after the `Other Bookmarks` `<H3>` and `<A>` items without any kind of separator, so it is not possible to differentiate between them (the `Other bookmarks` and `Mobile Bookmarks`) from within the HTML file.

#### Bookmark file structure

```html
[Netscape Bookmark File Headers]
<H1>Bookmarks</H1> <!-- Different H1 Content than Firefox -->
<DL><p>
    <!-- Folder containing the PERSONAL_TOOLBAR_FOLDER attribute set to true is the "Bookmarks bar"
     folder -->
    <DT><H3 PERSONAL_TOOLBAR_FOLDER="true"></H3>
    <DL><p>
        <!-- Contents of "Bookmarks bar" -->
        <DT><H3></H3>
        <DT><A></A>
    </DL><p>
    <!-- All the "H3" and "A" tags that come after the "Bookmarks bar" "H3" folder,
     and are in the main list, are links and folder from inside the "Other bookmarks" folder -->
    <DT><H3></H3>
    <DL><p>
        <DT><H3></H3>
        <DT><A></A>
    </DL><p>
    <DT><A></A>
    <!-- Chrome appends the "Mobile bookmarks" folder items (<H3> and <A>) after the "Other bookmarks"
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
#### Folder
```html
<DT><H3 ADD_DATE="1599759836" LAST_MODIFIED="0">Social</H3>
```
the folder can also contain an addition attribute that states the *special* role of the folder:
- `PERSONAL_TOOLBAR_FOLDER="true"`: for the `Bookmarks bar` folder.

#### URL
```html
<DT><A HREF="https://www.mozilla.org/en-US/contribute/" ADD_DATE="1599750431" ICON="data:image/png;base64,PHN2ZyB4bWxucz0naHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmcnIHdpZHRoPScxNicgaGVpZ2h0PScxNic+IDxwYXRoIGQ9J00wIDBoMTZ2MTZIMHonLz4gPHBhdGggZD0nTTEzLjk5NCAxMC4zNTZIMTVWMTJoLTMuMTcxVjcuNzQxYzAtMS4zMDgtLjQzNS0xLjgxLTEuMjktMS44MS0xLjA0IDAtMS40Ni43MzctMS40NiAxLjh2Mi42M2gxLjAwNlYxMkg2LjkxOFY3Ljc0MWMwLTEuMzA4LS40MzUtMS44MS0xLjI5MS0xLjgxLTEuMDM5IDAtMS40NTkuNzM3LTEuNDU5IDEuOHYyLjYzaDEuNDQxVjEySDF2LTEuNjQ0aDEuMDA2VjYuMDc5SDFWNC40MzVoMy4xNjh2MS4xMzlhMi41MDcgMi41MDcgMCAwIDEgMi4zLTEuMjlBMi40NTIgMi40NTIgMCAwIDEgOC45MzEgNS45MSAyLjUzNSAyLjUzNSAwIDAgMSAxMS40IDQuMjg0IDIuNDQ4IDIuNDQ4IDAgMCAxIDE0IDYuOXYzLjQ1OHonIGZpbGw9JyNmZmYnLz4gPC9zdmc+">Get Involved</A>
```
The `ICON` attribute is optional and sometimes not included.

### b. JSON

Chrome doesn't allow you to export or backup your bookmarks as a .json file, but you can get a copy of the .json file chrome stores your bookmarks in. Depending on your OS and browser (chrome/chromium), these are the locations of the file:

- `Linux [Chrome]` --> `~/.config/google-chrome`
- `Linux [Chromium]` --> `~/.config/chromium`
- `Mac OS X [Chrome]` --> `~/Library/Application Support/Google/Chrome`
- `Mac OS X [Chromium]` --> `~/Library/Application Support/Chromium`
- `Windows [Chrome]` --> `%LOCALAPPDATA%\Google\Chrome\User Data`
- `Windows [Chromium]` --> `%LOCALAPPDATA%\Chromium\User Data`

**NOTE:** Chrome's timestamps start from a different epoch than the Unix epoch (chrome counts in microseconds from `1601-01-01T00:00:00Z`).
You can convert the chrome epoch to Unix epoch by the following equation: `Unix Epoch = Chrome Epoch - 11644473600000000` (all values in the equation should be in milliseconds)

#### root Folder

The checksum in the root is calculated using MD5. For URL Nodes we add the `id`, `title`, and `url` to the checksum, which for the Folder Nodes we add the `id` and `title`.


```json5
{
  "version": 1,
  "sync_metadata": "",  // optional, base64 encoded str
  "roots": {
    "bookmark_bar": {}, // Folder Node
    "other": {},  // Folder Node
    "synced": {}, // Folder Node
    "meta_info": {},  // optional dict[str,str]
    "unsynced_meta_info": {}  // optional dict[str,str]
  },
  "checksum": "" // MD5 checksum as hex string
}
```

#### Folder

```json5
{
  "children": [], // Folder/URL Nodes
  "date_added": "13244233436520764",
  "date_last_used": "0",
  "date_modified": "0",
  "guid": "", // uuid as string
  "id": "1",
  "meta_info": {  // optional dict[str,str]
    "last_visited_desktop": "13204332604026373",
    "power_bookmark_meta": ""
  },
  "unsynced_meta_info": {}, // like meta_info it is an optional dict[str,str]
  "name": "Main Folder",
  "type": "folder"
}
```

#### URL

```json5
{
  "date_added": "13244224395000000",
  "date_last_used": "0",
  "guid": "", // uuid as string
  "id": "2",
  "meta_info": {  // optional dict[str,str]
    "last_visited_desktop": "13204918293394216",
    "power_bookmark_meta": ""
  },
  "unsynced_meta_info": {}, // like meta_info it is an optional dict[str,str]
  "name": "Google",
  "type": "url",
  "url": "https://www.google.com"
}
```

---
## 2. Firefox

The source code that contains all the bookmarks logic can found in the mozilla source code:
- [toolkit/components/places](https://searchfox.org/mozilla-central/source/toolkit/components/places)

**NOTE:** The `JSON` bookmarks file contains all folders, but doesn't show the Mobile folder in the desktop app's bookmarks manager.
However, you can find the mobile bookmarks if you search in the bookmarks manager for a bookmarked url.

### a. HTML

All the Firefox bookmarks in an HTML file are contained inside the main `<DL><p>` list.

All the `<H3>` and `<A>` items in the main list that don't contain special attributes set to `true` are items that are located inside the `Bookmarks Menu` folder.

The special folders `Bookmarks Toolbar` and `Other Bookmarks` in the main list, have a special attribute to indicate their type. 
The `Mobile Bookmarks` folder is not included in the HTML file when being exported (Firefox does not export `Mobile Bookmarks` to an HTML file), you need to export the bookmarks as JSON or use the firefox sqlite database file backup to export your `Mobile Bookmarks`.

#### Bookmark file structure

```html
[Netscape Bookmark File Headers]
<H1>Bookmarks Menu</H1> <!-- Different "H1" Content than Chrome -->

<DL><p>
    <!-- The <H3> and <A> tags inside the main <DL><p> are inside the "Bookmarks Menu" folder. -->
    <DT><H3></H3>
    <DT><A></A>
    <!-- Folder containing the PERSONAL_TOOLBAR_FOLDER attribute set to true is the "Bookmarks Toolbar"
    folder -->
    <DT><H3 PERSONAL_TOOLBAR_FOLDER="true"></H3>
    <DL><p>
        <!-- Contents of "Bookmarks Toolbar" -->
        <DT><H3></H3>
        <DT><A></A>
    </DL><p>
    <!-- Folder containing the UNFILED_BOOKMARKS_FOLDER attribute set to true is the "Other Bookmarks"
    folder -->
    <DT><H3 UNFILED_BOOKMARKS_FOLDER="true"></H3>
    <DL><p>
        <!-- Contents of "Other Bookmarks" -->
        <DT><H3></H3>
        <DT><A></A>
    </DL><p>
</DL><p>
```
#### Folder
```html
<DT><H3 ADD_DATE="1599750431" LAST_MODIFIED="1599750431">Mozilla Firefox</H3>
```
the folder can also contain an addition attribute that states the *special* role of the folder:
- `PERSONAL_TOOLBAR_FOLDER="true"`: for the `Toolbar` folder.
- `UNFILED_BOOKMARKS_FOLDER="true"`: for the `Other Bookmarks` folder.

#### URL
```html
<DT><A HREF="https://www.mozilla.org/en-US/contribute/" ADD_DATE="1599750431" LAST_MODIFIED="1599750431" ICON_URI="fake-favicon-uri:https://www.mozilla.org/en-US/contribute/" ICON="data:image/png;base64,PHN2ZyB4bWxucz0naHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmcnIHdpZHRoPScxNicgaGVpZ2h0PScxNic+IDxwYXRoIGQ9J00wIDBoMTZ2MTZIMHonLz4gPHBhdGggZD0nTTEzLjk5NCAxMC4zNTZIMTVWMTJoLTMuMTcxVjcuNzQxYzAtMS4zMDgtLjQzNS0xLjgxLTEuMjktMS44MS0xLjA0IDAtMS40Ni43MzctMS40NiAxLjh2Mi42M2gxLjAwNlYxMkg2LjkxOFY3Ljc0MWMwLTEuMzA4LS40MzUtMS44MS0xLjI5MS0xLjgxLTEuMDM5IDAtMS40NTkuNzM3LTEuNDU5IDEuOHYyLjYzaDEuNDQxVjEySDF2LTEuNjQ0aDEuMDA2VjYuMDc5SDFWNC40MzVoMy4xNjh2MS4xMzlhMi41MDcgMi41MDcgMCAwIDEgMi4zLTEuMjlBMi40NTIgMi40NTIgMCAwIDEgOC45MzEgNS45MSAyLjUzNSAyLjUzNSAwIDAgMSAxMS40IDQuMjg0IDIuNDQ4IDIuNDQ4IDAgMCAxIDE0IDYuOXYzLjQ1OHonIGZpbGw9JyNmZmYnLz4gPC9zdmc+">Get Involved</A>
```
The two attributes `ICON_URI` and `ICON` are optional and sometimes not included.


### b. JSON

Firefox allows users to export the bookmarks as a JSON file.
The `.json` file has a root folder, which has the following folders as children:

- `menu` : which is the "Bookmarks Menu" folder.
- `toolbar` : which is the "Bookmarks Toolbar" folder.
- `unfiled` : which is the "Other Bookmarks" folder.
- `mobile` : which is the "Mobile Bookmarks" folder.

#### Special Folder

Special folder and main folders like `menu` or `toolbar`, they contain extra fields to the standard Folder element, or different values to the standard fields.
The different special folders, the fields, and their values can be found in the table below:

| Special Folder \ Field Name |     `guid`     |  `title`  |          `root`          |
|:----------------------------|:--------------:|:---------:|:------------------------:|
| root                        | `root________` |    ` `    |       `placesRoot`       |
| menu                        | `menu________` |  `menu`   |  `bookmarksMenuFolder`   |
| toolbar                     | `toolbar_____` | `toolbar` |     `toolbarFolder`      |
| unfiled                     | `unfiled_____` | `unfiled` | `unfiledBookmarksFolder` |
| mobile                      | `mobile______` | `mobile`  |      `mobileFolder`      |


```json5
{
  "guid": "root________",
  "title": "",
  "index": 0,
  "dateAdded": 1639655814193000,
  "lastModified": 1678636423146000,
  "id": 1,
  "typeCode": 2,
  "type": "text/x-moz-place-container",
  "root": "placesRoot",
  "children": []
}
```

#### Folder

```json5
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

#### URL

```json5
{
  "guid": "7TpRGhofxKDv",
  "title": "Google",
  "index": 0,
  "dateAdded": 1599750431776000,
  "lastModified": 1599750431776000,
  "id": 2,
  "typeCode": 1,
  "iconuri": null,
  "type": "text/x-moz-place",
  "uri": "https://www.google.com"
}
```

---
## 3. Custom (Bookmarkie)

This is a custom format that is used by `BookmarksConverter`.
It supports the formats: `DB`, `HTML`, `JSON`

### a. DB

The `db` format uses the sqlite database.
The database puts both folders and urls in a Single Table Inheritance created using SQLAlchemy.
The Table schema is shown below:
```sqlite
create table bookmark
(
    id             INTEGER not null
        primary key,
    guid           VARCHAR
        unique,
    title          VARCHAR,
    "index"        INTEGER,
    parent_id      INTEGER
        references bookmark,
    date_added     INTEGER not null,
    date_modified  INTEGER not null,
    type           VARCHAR,
    special_folder VARCHAR
        unique,
    url            VARCHAR,
    icon           VARCHAR,
    icon_uri       VARCHAR,
    tags           VARCHAR
);
```

The relationship between an element and it's parent containing folder is achieved by a SQLAlchemy relationship (parent - children).
This relationship is not seen in the schema above.

The fields of each type (folder or url) are shown in the next sections.

#### Folder

The folder fields:
- id
- guid
- title
- index
- parent_id
- date_added
- date_modified
- type
- parent (this is a relationship field that is not shown in the schema)
- children (this is a relationship field that is not shown in the schema)
- special_folder

#### URL

The url fields:
- id
- guid
- title
- index
- parent_id
- date_added
- date_modified
- type
- url
- icon
- icon_uri
- tags

### b. HTML

The BookmarksConverter HTML format mimics the Firefox HTML format but also exports the `Mobile Bookmarks` folder.
All the bookmarks in the HTML file are contained inside the main `<DL><p>` list.

All the `<H3>` and `<A>` items in the main list that don't contain special attributes set to `true` are items that are located inside the `Bookmarks Menu` folder.

The special folders `Bookmarks Toolbar`, `Other Bookmarks`, and `Mobile Bookmarks` in the main list, have a special attribute to indicate their type. 

#### Bookmark file structure

```html
[Netscape Bookmark File Headers]
<H1>Bookmarks Menu</H1> <!-- Different "H1" Content than Chrome -->

<DL><p>
    <!-- The <H3> and <A> tags inside the main <DL><p> are inside the "Bookmarks Menu" folder. -->
    <DT><H3></H3>
    <DT><A></A>
    <!-- Folder containing the PERSONAL_TOOLBAR_FOLDER attribute set to true is the "Bookmarks Toolbar"
    folder -->
    <DT><H3 PERSONAL_TOOLBAR_FOLDER="true"></H3>
    <DL><p>
        <!-- Contents of "Bookmarks Toolbar" -->
        <DT><H3></H3>
        <DT><A></A>
    </DL><p>
    <!-- Folder containing the UNFILED_BOOKMARKS_FOLDER attribute set to true is the "Other Bookmarks"
    folder -->
    <DT><H3 UNFILED_BOOKMARKS_FOLDER="true"></H3>
    <DL><p>
        <!-- Contents of "Other Bookmarks" -->
        <DT><H3></H3>
        <DT><A></A>
    </DL><p>
    <!-- Folder containing the MOBILE_BOOKMARKS_FOLDER attribute set to true is the "Mobile Bookmarks"
    folder -->
    <DT><H3 MOBILE_BOOKMARKS_FOLDER="true"></H3>
    <DL><p>
        <!-- Contents of "Mobile Bookmarks" -->
        <DT><H3></H3>
        <DT><A></A>
    </DL><p>
</DL><p>
```
#### Folder
```html
<DT><H3 ADD_DATE="1599750431" LAST_MODIFIED="1599750431">Mozilla Firefox</H3>
```
the folder can also contain an addition attribute that states the *special* role of the folder:
- `PERSONAL_TOOLBAR_FOLDER="true"`: for the `Toolbar` folder.
- `UNFILED_BOOKMARKS_FOLDER="true"`: for the `Other Bookmarks` folder.
- `MOBILE_BOOKMARKS_FOLDER="true"`: for the `Mobile Bookmarks` folder.

#### URL
```html
<DT><A HREF="https://www.mozilla.org/en-US/contribute/" ADD_DATE="1599750431" LAST_MODIFIED="1599750431" ICON_URI="fake-favicon-uri:https://www.mozilla.org/en-US/contribute/" ICON="data:image/png;base64,PHN2ZyB4bWxucz0naHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmcnIHdpZHRoPScxNicgaGVpZ2h0PScxNic+IDxwYXRoIGQ9J00wIDBoMTZ2MTZIMHonLz4gPHBhdGggZD0nTTEzLjk5NCAxMC4zNTZIMTVWMTJoLTMuMTcxVjcuNzQxYzAtMS4zMDgtLjQzNS0xLjgxLTEuMjktMS44MS0xLjA0IDAtMS40Ni43MzctMS40NiAxLjh2Mi42M2gxLjAwNlYxMkg2LjkxOFY3Ljc0MWMwLTEuMzA4LS40MzUtMS44MS0xLjI5MS0xLjgxLTEuMDM5IDAtMS40NTkuNzM3LTEuNDU5IDEuOHYyLjYzaDEuNDQxVjEySDF2LTEuNjQ0aDEuMDA2VjYuMDc5SDFWNC40MzVoMy4xNjh2MS4xMzlhMi41MDcgMi41MDcgMCAwIDEgMi4zLTEuMjlBMi40NTIgMi40NTIgMCAwIDEgOC45MzEgNS45MSAyLjUzNSAyLjUzNSAwIDAgMSAxMS40IDQuMjg0IDIuNDQ4IDIuNDQ4IDAgMCAxIDE0IDYuOXYzLjQ1OHonIGZpbGw9JyNmZmYnLz4gPC9zdmc+">Get Involved</A>
```
The two attributes `ICON_URI` and `ICON` are optional and sometimes not included.

### c. JSON

If you export your bookmarks as a json file using this BookmarksConverter package, you will get a json format that will look as follows:

#### Special Folder

The special folder contains the extra field `special_folder` that can have one of the following values depending on it's type.
- root: `root`
- Bookmarks Menu: `menu`
- Bookmarks Toolbar: `toolbar`
- Other Bookmarks: `other`
- Mobile Bookmarks: `mobile`

```json5
{
  "id": 5,
  "guid": "c4c8030c-2dc9-4236-b728-cd5cb440b3de",
  "index": 3,
  "title": "Other bookmarks",
  "date_added": 1659184459926000,
  "date_modified": 1678636323216000,
  "type": "folder",
  "special_folder": "other",
  "children": []
}
```

#### Folder

```json5
{
  "id": 5,
  "guid": "c4c8030c-2dc9-4236-b728-cd5cb440b3de",
  "index": 3,
  "title": "Some title",
  "date_added": 1659184459926000,
  "date_modified": 1678636323216000,
  "type": "folder",
  "children": []
}
```

#### URL

```json5
{
  "id": 23,
  "guid": "c4c8030c-2dc9-4236-b728-cd5cb440b3de",
  "index": 0,
  "title": "Welcome to Python.org",
  "date_added": 1599750592000000,
  "date_modified": 1599750592000000,
  "url": "https://www.python.org/",
  "icon": "",
  "iconuri": "",
  "tags": [],
  "type": "url"
}
```
