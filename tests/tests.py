import pytest
from generateHtml.tags import *
from generateHtml.attributes import *
from generateHtml.exceptions import *


def test_initialize_tags():
    assert "<p>\n</p>" == str(P())
    assert "<p>\n  Paragraph\n</p>" == str(P("Paragraph"))
    assert "<div>\n  <p>\n    Paragraph\n  </p>\n</div>" == str(Div(P("Paragraph")))

    with pytest.raises(IllegalCompositionError):
        Hr(P("text"))


def test_display_function():
    assert "<div><p>Paragraph</p></div>" == Div(P("Paragraph")).display(pretty=False)
    assert "<div>\n <p>\n  Paragraph\n </p>\n</div>" == Div(P("Paragraph")).display(
        indent=" "
    )


def test_initialize_text():
    assert "Text" == str(Text("Text"))
    assert "1" == str(Text(1))
    assert "1.0" == str(Text(1.0))
    assert "" == str(Text(""))
    assert "" == str(Text(None))


def test_initialize_attributes():
    assert 'id="new_id"' == str(Id("new_id"))
    assert 'id="1"' == str(Id(1))
    assert "required" == str(Required())
    assert 'required="required"' == str(Required("", "repeated"))
    assert 'required=""' == str(Required("", "empty"))
    assert 'class="new_class second_class"' == str(Class("new_class", "second_class"))
    assert 'accept-charset="utf-8"' == str(AcceptCharset("utf-8"))

    with pytest.raises(DuplicateAttributeError):
        P("text", Id("1"), Id("2"))

    with pytest.raises(WrongAttributeElementCombinationError):
        P(Src("index.html"))


def test_initialize_styles():
    assert 'style="color: black;font-size: 20 px;"' == str(
        Style_(color="black", font_size="20 px")
    )
    assert 'style="color: black;font-size: 20 px;"' == str(
        Style_("color: black;font-size: 20 px;")
    )


def test_comments():
    assert "<!--<p>Paragraph</p>-->" == Comment(P("Paragraph")).display(pretty=False)
    assert "<!--[if lt IE 9]><p>Paragraph</p><![endif]-->" == Comment(
        P("Paragraph"), condition="lt IE 9"
    ).display(pretty=False)


def test_initialize_named_arguments():
    assert '<p id="new_id" class="container">\n</p>' == str(
        P(id="new_id", class_="container")
    )
    assert '<p data="data-item" data-row="1">\n</p>' == str(
        P(data="data-item", data_row=1)
    )


def test_tag_getitem():
    p: HtmlElement = P("Text", Class("paragraph_class"), Span("span", Id("span_id")))
    assert (
        '<p class="paragraph_class">\n  Text\n  <span id="span_id">\n    span\n  </span>\n</p>'
        == str(p)
    )

    assert "Text" == str(p[0])
    assert 'class="paragraph_class"' == str(p["class"])
    assert 'id="span_id"' == str(p[1]["id"])


def test_tag_setitem():
    p: HtmlElement = P("Text", Class("paragraph_class"), Span("span", Id("span_id")))
    assert (
        '<p class="paragraph_class">\n  Text\n  <span id="span_id">\n    span\n  </span>\n</p>'
        == str(p)
    )

    p[0] = "Changed text"
    assert "Changed text" == str(p[0])

    p[0] = Text("Changed text node")
    assert "Changed text node" == str(p[0])

    p[0] = Paragraph("Changed text in paragraph")
    assert "<p>\n  Changed text in paragraph\n</p>" == str(p[0])

    sp = p[1]
    sp["id"] = "new_id"
    assert '<span id="new_id">\n  span\n</span>' == str(sp)


def test_tag_delitem():
    p: HtmlElement = P("Text", Class("paragraph_class"), Span("span", Id("span_id")))
    assert (
        '<p class="paragraph_class">\n  Text\n  <span id="span_id">\n    span\n  </span>\n</p>'
        == str(p)
    )

    del p[0]
    assert (
        '<p class="paragraph_class">\n  <span id="span_id">\n    span\n  </span>\n</p>'
        == str(p)
    )

    del p[0]["id"]
    assert '<p class="paragraph_class">\n  <span>\n    span\n  </span>\n</p>' == str(p)


def test_tag_operators_manipulation():
    em: HtmlElement = Em("emphasized")
    strong: HtmlElement = Strong("strong")

    assert "<em>\n  emphasized\n</em>\n<strong>\n  strong\n</strong>" == str(
        em + strong
    )
    assert "<strong>\n  strong\n</strong>\n<em>\n  emphasized\n</em>" == str(
        strong + em
    )
    assert "<strong>\n  strong\n</strong>\n<strong>\n  strong\n</strong>" == str(
        strong * 2
    )

    em += Hr()  # Creates Container class
    assert "<em>\n  emphasized\n</em>\n<hr>" == str(em)


def test_context_manager():
    p: HtmlElement = None
    with P("Text") as p:
        Class("paragraph_class")
        Span("span", Id("span_id"))

    assert (
        '<p class="paragraph_class">\n  Text\n  <span id="span_id">\n    span\n  </span>\n</p>'
        == str(p)
    )

    p: HtmlElement = None
    with P() as p:
        sp = Span()
        sp.add("span").add(Id("span_id"))

        t = "Text"
        p.add(Class("paragraph_class"))

        p.add(t, sp)

    assert (
        '<p class="paragraph_class">\n  Text\n  <span id="span_id">\n    span\n  </span>\n</p>'
        == str(p)
    )

    p: HtmlElement = None
    with P() as p, Span() as sp:
        Text("span")
        Id("span_id")

        p.add(Class("paragraph_class"))
        p.add("Text")

    assert (
        '<p class="paragraph_class">\n  Text\n  <span id="span_id">\n    span\n  </span>\n</p>'
        == str(p)
    )
