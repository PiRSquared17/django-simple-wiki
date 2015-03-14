## Contents ##



# PRESENTING! DJANGO-WIKI -> #

A new and more modern wiki has seen the light and you are highly encouraged to use it instead of this.

## [Check out django-wiki over at Github](https://github.com/benjaoming/django-wiki) ##

# Introduction #
Hierarchical, relational Wiki with permission system, revision control and file attachments. Much similar to Trac Wiki.

The application is made to be easy to integrate with existing websites. But you should keep in mind when extending and possibly overwriting models etc. that your version will become hard to update. This is relevant because simple-wiki is still under heavy development.

TODOs:

  * Use South migrations
  * Put templates in their own directory
  * Use URL namespace

# Features #

  * Quick and easy default user interface
  * Hierarchy. An article can contain children.
  * Relational. Articles have symmetrical relations, making navigation easy on the user.
  * Permission system using the hierarchy of articles. Makes it possible to create `/foo/bar` and add special permissions to `bar` or inherit from `foo`.
  * Revision system, in which the contents of each edit action is saved, so it can be reverted.
  * Attachments. All file types can be attached and will be (hopefully) safely stored in filesystem.

[![](http://django-simple-wiki.googlecode.com/files/screenshot_thumb.jpg)](http://wikidemo.overtag.dk)

# Help! #

Please join the team or send patches! There's lots of room for improvements. See current issues for full inspiration or add your own.

One of the main features to be added, is search functionality.

Currently, contributions from people with JS and CSS experience are very appreciated. The frontend should have a better look-and-feel, still maintaining the general purpose. For instance by implementing a new frontend in JQuery.

Translations are not very handy at the moment, since many of the default messages are not properly worked out, and new messages will be added.

# Requirements #

  * Markdown 2+ ("pip install markdown")
  * Django 1.1 - 1.3.1 (Not tested with 1.4 -- any results?)

# Installation #

```
$ svn checkout http://django-simple-wiki.googlecode.com/svn/trunk/ django-simple-wiki
$ svn export django-simple-wiki PATH_TO_DJANGO_PROJECT/simplewiki
```

Any subsequent updates can be made with `svn up` from the checkout dir, adding `--force` to the subversion export command. But **beware** that this overwrites any changes you have made to the source code.

To setup simple-wiki, add the following line to your `urls.py`. Please note, that simplewiki does not currently support installation in root directory (see [issue 2](http://code.google.com/p/django-simple-wiki/issues/detail?id=2)). Also note the trailing slash.

```
    (r'^wiki/', include('simplewiki.urls')),
```

You need to create a symbolic link to the media files, that simple-wiki uses and make the attachment directory writable:

```
$ cd YOUR_MEDIA_ROOT
$ ln -s PATH_TO_DJANGO_PROJECT/simplewiki/media simplewiki
$ chmod 777 simplewiki/attachments
```

# Demo #

A demo can be found here: [wikidemo.overtag.dk](http://wikidemo.overtag.dk)

[![](http://media.djangoproject.com/img/badges/djangoproject120x25_grey.gif)](http://www.djangoproject.com/)

&lt;wiki:gadget url="http://www.ohloh.net/p/587336/widgets/project\_users.xml" height="100" border="0"/&gt;