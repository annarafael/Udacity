#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
from string import letters
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext import db

import jinja2
import os
#import cgi
import re

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape = True)


form = """
        <form method="post" action="/testform">
        <input name="q">
        <input type="submit">
        </form>"""


formRot13 = """
      <form method="post" action="/rot13">
      <textarea name="text"
                style="height: 100px; width: 400px;"></textarea>
      <br>
      <input type="submit">
      </form>
      """

formsignup = """
      <form method="post" action="/signup">
      <label>Username <input name="username"> </label> %(usrerror)s <br>
      <label>Password <input name="password"> </label> %(pwerror)s <br>
      <label>Renter Password <input name="repassword"> %(repwerror)s </label> <br>
      <label>Email(Optional) <input name="email"> %(emailerror)s </label> <br>
      <br>
      <input type="submit">
      </form>
      """
    
class MainHandler(webapp.RequestHandler):
    def get(self):
        self.response.headers["Content-Type"] = 'text/html'
        self.response.out.write(formRot13)
        
class Welcome(webapp.RequestHandler):
    def get(self):
        username = self.request.get("username")

        self.response.out.write("Thanks! %s" %username)
   

class SignupHandler(webapp.RequestHandler):
    def valid_email(self,username):
        USER_RE = re.compile(r"^[\S]+@[\S]+\.[\S]+$")
        return USER_RE.match(username)

    def valid_password(self,username):
        USER_RE = re.compile(r"^.{3,20}$")
        return USER_RE.match(username)

        
    def valid_username(self,username):
        USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
        return USER_RE.match(username)
    
    def get(self,error=""):
        error_keys = {'usrerror':"",'repwerror':"",'pwerror':"",'emailerror':""}
        self.response.headers["Content-Type"] = 'text/html'
        self.response.out.write(formsignup % error_keys)
    
    def post(self,usrerror="",pwerror="",emailerror=""):
        error_keys = {'usrerror':"",'repwerror':"",'pwerror':"",'emailerror':""}
        error = 0

        username = self.request.get("username")
        password = self.request.get("password")
        repassword = self.request.get("repassword")
        email = self.request.get("email")
        
        if not self.valid_username(username):
            error = error + 1
            error_keys['usrerror'] = "Error: Invalid UserName!"
            
        
        if not self.valid_password(password):
            error = error + 1
            error_keys['pwerror'] = "Error: Invalid Password!"

        
        if repassword != password:
            error = error + 1
            error_keys['repwerror'] = "Error: Password not matching!"
        
        
        if email != "":
            if not self.valid_email(email):
                error = error + 1
                error_keys['emailerror'] = "Error: Invalid Email!"
            
        if error > 0:
            self.response.out.write(formsignup % error_keys)
        else:
            self.redirect("/welcome?username="+username)

class Rot13Handler(webapp.RequestHandler):
    def get(self):
        self.response.headers["Content-Type"] = 'text/html'
        self.response.out.write(formRot13)
        
    def Rot13(self,user_text):
        rot13_dict = {'a': 'n', 'c': 'p', 'b': 'o', 'e': 'r', 'd': 'q', 'g': 't', 'f': 's', 'i': 'v', 'h': 'u', 'k': 'x', 'j': 'w', 'm': 'z', 'l': 'y', 'o': 'b', 'n': 'a', 'q': 'd', 'p': 'c', 's': 'f', 'r': 'e', 'u': 'h', 't': 'g', 'w': 'j', 'v': 'i', 'y': 'l', 'x': 'k', 'z': 'm'}
        #text = cgi.escape(user_text)
        text = user_text
        new_text = ''
        for a in text:
            try:
                if a.isupper():
                    new_text = new_text + rot13_dict[a.lower()].upper()
                else:
                    new_text = new_text + rot13_dict[a]
            except:
                new_text = new_text + a
        #return cgi.escape(new_text)
        return new_text
    
    def post(self):
        text = self.request.get("text")
        text = self.Rot13(text)
        self.response.out.write(text)
        #self.response.headers["Content-Type"] = 'text/plain'
        #self.response.out.write(self.request)



class TestHandler(webapp.RequestHandler):
    def post(self):
        q = self.request.get("q")
        self.response.out.write(q)
        #self.response.headers["Content-Type"] = 'text/plain'
        #self.response.out.write(self.request)


###################################
#	Blog Start 
###################################


def render_str(template, **params):
    t = jinja_env.get_template(template)
    return t.render(params)

class BaseHandler(webapp.RequestHandler):
    def render(self, template, **kw):
        self.response.out.write(render_str(template, **kw))

    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)


class Blog(db.Model):
	subject = db.StringProperty(required = False)
	content = db.TextProperty(required = True)
	created = db.DateTimeProperty(auto_now_add = True)


class NewPostHandler(BaseHandler):
	def render_front(self,subject="",content="",error=""):
		blogs = db.GqlQuery("SELECT * from Blog ORDER BY created desc")
		self.render("blog-form.html",subject=subject,content=content,error=error,blogs=blogs)

	def get(self):
		self.render_front()

	def post(self):
		subject = self.request.get("subject")
		content = self.request.get("content")
		#content = content.replace("\n",'<br>')
		
		if subject and content:
			a = Blog(subject = subject, content = content)
			a.put()
			page = str(a.key().id())
			self.redirect("/blog/%s" % page)
		else:
			error = "Both subject and content should be filled"
			self.render_front(subject=subject,content=content,error=error)

class PostHandler(BaseHandler):
	"handles permalink to the posts"
	def get(self,post_id):
		key = db.Key.from_path('Blog',int(post_id))
		post = db.get(key)

		if not post:
			self.write("404 Page not found")
			return

		self.render("blog-page.html",blog=post)
			

class BlogHandler(BaseHandler):
	def render_front(self,subject="",content="",error=""):
		blogs = db.GqlQuery("SELECT * from Blog ORDER BY created desc LIMIT 10")
		self.render("blog-front.html",subject=subject,content=content,error=error,blogs=blogs)

	def get(self):
		self.render_front()

	def post(self):
		self.redirect("/blog")


def main():
    application = webapp.WSGIApplication([('/', MainHandler),
                                          ('/blog',BlogHandler),
                                          ('/blog/([0-9]+)',PostHandler),
                                          ('/blog/newpost',NewPostHandler),
                                          ('/testform',TestHandler),
                                          ('/signup',SignupHandler),
                                          ('/welcome',Welcome),
                                          ('/rot13',Rot13Handler)],
                                         debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()
