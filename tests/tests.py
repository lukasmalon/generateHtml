import pytest
from generateHtml.tags import *
from generateHtml.attributes import *
from generateHtml.exceptions import *
from generateHtml import utils


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

def test_name_to_string():
    assert "id" == Id("id1").name_to_string()
    assert "required" == Required().name_to_string()
    assert "accept-charset" == AcceptCharset("utf-8").name_to_string()
    assert "data-id" == Data_("id", "value").name_to_string()
    assert "class" == Class("class1", "class2").name_to_string()

def test_check_attribute_value():
    assert "value" == HtmlAttribute.check_attribute_value("value")
    assert "1" == HtmlAttribute.check_attribute_value(1)
    assert "1.0" == HtmlAttribute.check_attribute_value(1.0)

    with pytest.raises(TypeError):
        HtmlAttribute.check_attribute_value(None)

    with pytest.raises(TypeError):
        HtmlAttribute.check_attribute_value([])

def test_attribute_value():
    attr = Id('id1')
    assert 'id="id1"' == str(attr)
    attr.add("id2")
    assert 'id="id1id2"' == str(attr)

    attr.value = "id3"
    assert 'id="id3"' == str(attr)
    attr.value = 3
    assert 'id="3"' == str(attr)

    with pytest.raises(ValueError):
        attr.add(None)

def test_attribute_name():
    attr = Id('id1')
    assert "id" == attr.name

def test_initialize_attributes():
    assert 'id="new_id"' == str(Id("new_id"))
    assert 'id="1"' == str(Id(1))
    assert 'class="new_class second_class"' == str(Class("new_class", "second_class"))
    assert 'accept-charset="utf-8"' == str(AcceptCharset("utf-8"))

    with pytest.raises(DuplicateAttributeError):
        P("text", Id("1"), Id("2"))

    with pytest.raises(WrongAttributeElementCombinationError):
        P(Src("index.html"))

def test_initialize_boolean_attributes():
    assert 'required' == str(Required(true_value=BooleanTrueDisplayOption.SHORT))
    assert 'required=""' == str(Required(true_value=BooleanTrueDisplayOption.EMPTY))
    assert 'required="required"' == str(Required(true_value=BooleanTrueDisplayOption.REPEATED))
    assert 'required="value"' == str(Required(true_value="value"))

    with pytest.raises(ValueError):
        str(Required(true_value=1))

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


def test_table_initialization():
    t1 = Table(
        Tr(Th('Col 1'), Th('Col 2'), Th('Col 3')),
        Tr(Td(1), Td(2), Td(3)),
        Tr(Td(4), Td(5), Td(6)),
    )
    assert "<table><tr><th>Col 1</th><th>Col 2</th><th>Col 3</th></tr><tr><td>1</td><td>2</td><td>3</td></tr><tr><td>4</td><td>5</td><td>6</td></tr></table>"\
        == t1.display(pretty=False)
    
    t2 = Table(
        [[1, 2, 3], [4, 5, 6]], header=['Col 1', 'Col 2', 'Col 3']
    )

    assert "<table><tr><th>Col 1</th><th>Col 2</th><th>Col 3</th></tr><tr><td>1</td><td>2</td><td>3</td></tr><tr><td>4</td><td>5</td><td>6</td></tr></table>"\
        == t2.display(pretty=False)

    t3 = Table(
        [['Col 1', 'Col 2', 'Col 3'], [1, 2, 3], [4, 5, 6]], header='row'
    )
    assert "<table><tr><th>Col 1</th><th>Col 2</th><th>Col 3</th></tr><tr><td>1</td><td>2</td><td>3</td></tr><tr><td>4</td><td>5</td><td>6</td></tr></table>"\
        == t3.display(pretty=False)

    t4 = Table(
        [['Col 1', 'Col 2'], [1, 2], [3, 4]], header='col'
    )
    assert "<table><tr><th>Col 1</th><td>Col 2</td></tr><tr><th>1</th><td>2</td></tr><tr><th>3</th><td>4</td></tr></table>"\
        == t4.display(pretty=False)

def test_find():
    inner_div = Div(Id("inner_div"))
    li_list = [Li(i) for i in range(10)]
    paragraph = P("Foo bar baz")
    em = Em("bar")

    div = Div(
    paragraph,
    Img(Src("img.png")),
    Id("foo"),
    Ol(Class("bar"),
    *li_list),
    em,
    inner_div)

    assert [div, inner_div] == div.find(Div()) # Finds all divs in div (including self)
    # return 2 divs: [<:: Div element: 4 child nodes, 1 attributes ::>, <:: Div element: no childs, 1 attributes ::>]

    assert [inner_div] == div.find(Div(Id("inner_div"))) # Finds all divs with id="inner_div"
    # return 1 div: [<:: Div element: no childs, 1 attributes ::>]

    assert [li_list[1]] == div.find(Li(1)) # Finds all li with text "1"
    # return 1 li: [<:: Li element: 1 child nodes ::>]

    assert [paragraph[0], em[0]] == div.find("bar") # Finds all Text nodes containing 'bar'
    # return 2 Text nodes: [<:: Text: "Foo bar ba..." ::>, <:: Text: "bar" ::>]

def test_prepend_dash():
    assert '-Accept-Charset' == utils.prepend_dash_before_uppercase('AcceptCharset')
    assert '-Data' == utils.prepend_dash_before_uppercase('Data')

def test_escape_html():
    assert '&lt;p&gt;' == utils.escape_html('<p>')
    assert '&lt;&amp;&#34;&gt;' == utils.escape_html('<&">')
    assert "&#39;" == utils.escape_html("'")

def test_unescape_html():
    assert '<p>' == utils.unescape_html('&lt;p&gt;')
    assert '<&">' == utils.unescape_html('&lt;&amp;&#34;&gt;')
    assert "'" == utils.unescape_html("&#39;")

def test_context_manager():
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
