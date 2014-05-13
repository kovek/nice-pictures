# notporn.py
# Description: Fetch the 25 most popular links in the sfwporn subreddits
# Note: This script does not have the best possible method to do this work.
# For example, videos did not get downloaded. Also, there are many other sources
# like flickr or devianart from which downloading a photo is not as simple
# as downloading from imgur.

import os # To interact with the hard disk files
import pycurl # To interact with the internet
import StringIO # For a buffer required for pycurl

allNames = open('sfwpornsubreddits') # Import the file with all of the sfwporn subreddits.
namesList = allNames.read().split('\n') # Split the file where there are new lines 
										# Into a list of strings that look like "/r/subreddit" 
for name in namesList:
# I think that you can also do for line in allNames instead.
	c = pycurl.Curl() # Create an object to access the internet
	b = StringIO.StringIO() # Create a buffer(Or is it not?) to read the contents of webpages
	c.setopt(pycurl.WRITEFUNCTION, b.write) 
	# The pycurl.Curl class lets you modify its configurations
	# Here, we are changing the write function to the one referenced 
	# by b.write

	directory = name[3:] # The directory into which we will send the
	# files is named after the subreddit's name

	try:
		os.mkdir(directory) # Create a directory
	except OSError:
		print "dir already exists"
		continue
		# Skip to the next subreddit
		# Instead of just skipping the directory

	infoFile = open(os.curdir+os.sep+directory+os.sep+'info.txt', 'a+')
	# Create an info file in the directory
	# I thought it would be best to let the observer of the images have a somewhat quick access
	# to the reddit post related to the picture.

	url = "http://www.reddit.com"+name+"/top.rss?sort=top&t=all"
	# This is the page where we will be looking
	# for the pictures

	c.setopt(pycurl.URL, url) # More configuring. If you want to know what these do,
	#take a look at pycurl's documentation 

	c.setopt(pycurl.FOLLOWLOCATION, 1) # Sometimes there was a 302 redirect,
	# so I needed to follow the to the location being pointed to

	c.perform() # Finally, load the page!
	thePageXML = b.getvalue() # Get the string out of that buffer
	index = thePageXML.find("[link]")
	# Note! This is a _horrible_ way to search for the link.
	# I suggest taking a look at a parser, like XMLTree

	while( index != -1 ): # Perform the "find a picture" loop until there are no more pictures to find
		# Basically, what the following lines do is that they find a string [link]...
		# ... then, it finds the first url before that [link] string. It queries that url and... 
		# ... stores the response into a .jpg file. Also, it takes the post's url and pairs it...
		# ... with the filename in the info.txt file inside of the subreddit's directory.
		# Sometimes, the posts cannot be properly downloaded, so the script just notifies the user...
		# ... simply by printing the link that did not work. Instead, it could log that information...

		# Let the ugly code begin....
		bb = StringIO.StringIO()
		c.setopt( pycurl.WRITEFUNCTION, bb.write )
		startIndex = thePageXML.rfind("http", 0, index)
		endIndex = thePageXML.find('&#34', startIndex)
		theLink = thePageXML[startIndex:endIndex]
		startPostIndex = thePageXML.rfind("http", 0, startIndex-1)
		startPostIndex = thePageXML.rfind("http", 0, startPostIndex-1)
		startPostIndex = thePageXML.rfind("http", 0, startPostIndex-1)
		endPostIndex = thePageXML.find('&#34',startPostIndex) 
		pageUrl = thePageXML[startPostIndex:endPostIndex]
		print pageUrl
		thePageXML = thePageXML[index+6:]
		index = thePageXML.find("[link]")
		fileName = theLink[theLink.rfind('/')+1:]
		infoFile.write(fileName+': '+pageUrl+'\n')
		if fileName.find('.jpg') == -1:
			theLink += '.png'	
		c.setopt(pycurl.URL, theLink)
		try:
			c.perform()
			open(os.curdir+os.sep+directory+os.sep+fileName,'w+').close()
			f = open( os.curdir + os.sep + directory + os.sep + fileName, 'wb')
			f.write( bb.getvalue() )
			f.close()
		except (IOError, pycurl.error) as e:
			print "This reddit post failed: " + pageUrl
			continue

