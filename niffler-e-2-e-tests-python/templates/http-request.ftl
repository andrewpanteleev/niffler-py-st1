<!DOCTYPE html>
<html lang="en">
<div>{% if request.method %}{{request.method}}{% else %}GET{% endif %} to {% if request.url %}{{request.url}}{% else %}None{% endif %}</div>

{% if request.body %}
    <h4>Body</h4>
    <div>
    <pre class="preformated-text">
    {{request.body}}
    </pre>
    </div>
{% endif %}

{% if request.headers %}
    <h4>Headers</h4>
    <div>
    {% for key, value in request.headers.items() %}
        <div>{{key}}: {{value}}</div>
    </div>
    {% endfor %}
{% endif %}

{% if request.cookies %}
    <h4>Cookies</h4>
    <div>
        {% for key, value in request.cookies.items() %}
        <div>{{key}}: {{value}}</div>
        {% endfor %}
    </div>
{% endif %}

{% if curl %}
    <h4>Curl</h4>
    <div>
        {{curl}}
    </div>
{% endif %}

{% if request.params %}
    <h4>QueryParams</h4>
    <div>
        {% for key, value in request.params.items() %}
        <div>{{key}}: {{value}}</div>
        {% endfor %}
    </div>
{% endif %}