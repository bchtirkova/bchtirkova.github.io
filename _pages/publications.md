---
layout: archive
title: "Publications"
permalink: /publications/
author_profile: true
read_more: true
---

{% include base_path %}

<div class="wordwrap">You can find a full list of my articles on <a href="{{site.author.googlescholar}}">my Google Scholar profile</a>.</div> 

------


Selected publications
======

Climate sensitivity
------

{% for post in site.publications reversed %}
{% if post.category == "sensitivity" %}
  {% include archive-single-publication.html %}
{% endif %}
{% endfor %}


Atmospheric shortwave radiation
------

{% for post in site.publications reversed %}
  {% if post.category == "shortwave" %}
    {% include archive-single-publication.html %}
  {% endif %}
{% endfor %}


Oceanography of the Black Sea
------

{% for post in site.publications reversed %}
{% if post.category == "blacksea" %}
  {% include archive-single-publication.html %}
{% endif %}
{% endfor %}

