GenerateHtml
========
`GenerateHtml` is library for creating HTML files using Python code.

By utilizing object-oriented principles this library allows users to construct HTML elements as Python objects, manage complex structures, and easily manipulate attributes, child nodes, and styles.

## Basic example

```python
# import tags and attributes
from generateHtml.tags import Div, H1, P, Hr
from generateHtml.attributes import Class

# both tags and attributes are represented by classes
div = Div(
    # tags can be nested inside another just by passing them as argument in constructor
    H1('Title'),
    P('Paragraph'),
    # attribute classes can be passed in constructor too
    Class('container'),
    # tags and attributes can be arranged freely in the constructor
    Hr()
)

# result can be displayed with python's print function
print(div)
```

**Output result**
```html
<div class="container">
  <h1>
    Title
  </h1>
  <p>
    Paragraph
  </p>
  <hr>
</div>
```

## HTML Tags
All HTML element tags are stored inside ``generateHtml.tags`` as separate classes named same as corresponding html element but with first letter uppercased.

Some tags have additional aliases classes inside ``generateHtml.tags`` implemented too:

| HTML Tag | Python class |
|:--------:|:-------------:|
| `<p>`    | `P, Paragraph` |

---

### Initialize
You can create nested HTML structure by just passing tag objects as constructor arguments:
```python
print(Div(H1(), Hr(), Paragraph()))
```

Outputs in:
```html
<div>
  <h1>
  </h1>
  <hr>
  <p>
  </p>
</div>
```

### Displaying
You can use built-in `__str__` for displaying result or method `display()` if you want to edit any of the displaying options.
```python
print(Div(H1("Header")).display(pretty=False))
```
```html
<div><h1>Header</h1></div>
```

### Text
For adding text into tags, you can just pass a `str` as argument into tag constructor:
```python
print(Paragraph("Text of the paragraph"))
```
Or you can use `Text` class:
```python
print(Paragraph(Text("Text of the paragraph")))
```

Outputs in same result:
```html
  <p>
    Text of the paragraph
  </p>
```

### Comments
For HTML comment section you can use class `Comment`:
```python
print(Comment("Happy commenting!", P("Can contain another tags too")))
```
```html
<!--
  Happy commenting!
  <p>
    Can contain another tags too
  </p>
-->
```

`Comment` class supports IE specific conditional comments:
```python
print(Comment("This is conditional comment", condition="IE 8"))
```
```html
<!--[if IE 8]>
  This is conditional comment
<![endif]-->
```

### Empty container
If you need to group some tags together (one after other) you can use `Container` class:
```python
print(Container(P("First paragraph"), P("Second paragraph")))
```
```html
<p>
  First paragraph
</p>
<p>
  Second paragraph
</p>
```

### Tables
You can initialize HTML table through `Table` tag class in multiple ways:

<details>

  <summary>Manually anotate every table data item</summary>

  ```python
  print(Table(
    Tr(Th('Col 1'), Th('Col 2'), Th('Col 3')),
    Tr(Td(1), Td(2), Td(3)),
    Tr(Td(4), Td(5), Td(6)),
  ))
  ```
  <table><tr><th>Col 1</th><th>Col 2</th><th>Col 3</th></tr><tr><td>1</td><td>2</td><td>3</td></tr><tr><td>4</td><td>5</td><td>6</td></tr></table>

  ```html
  <table>
    <tr>
      <th>
        Col 1
      </th>
      <th>
        Col 2
      </th>
      <th>
        Col 3
      </th>
    </tr>
    <tr>
      <td>
        1
      </td>
      <td>
        2
      </td>
      <td>
        3
      </td>
    </tr>
    <tr>
      <td>
        4
      </td>
      <td>
        5
      </td>
      <td>
        6
      </td>
    </tr>
  </table>
  ```
</details>

<details>
  <summary>Pass table data in constructor as list of lists</summary>

  ```python
  print(Table(
    [['Col 1', 'Col 2', 'Col 3'], [1, 2, 3], [4, 5, 6]]
  ))
  ```
  <table><tr><td>Col 1</td><td>Col 2</td><td>Col 3</td></tr><tr><td>1</td><td>2</td><td>3</td></tr><tr><td>4</td><td>5</td><td>6</td></tr></table>

You can pass header argument:
  ```python
    print(Table(
      [[1, 2, 3], [4, 5, 6]], header=['Col 1', 'Col 2', 'Col 3']
    ))
  ```

Or explicitly set first row/col or both as header:
```python
  print(Table(
    [['Col 1', 'Col 2', 'Col 3'], [1, 2, 3], [4, 5, 6]], header='row'
  ))
  ```
Both results in this table:
  <table><tr><th>Col 1</th><th>Col 2</th><th>Col 3</th></tr><tr><td>1</td><td>2</td><td>3</td></tr><tr><td>4</td><td>5</td><td>6</td></tr></table>

</details>

<!---
### Document container
For fast html page prototyping you can use `Document` class. It creates basic HTML page with `head` and `body` tags accesible via `Document` object properties. Adding tags into Document class will automatically adds everything into `body` tag.
```python
print(Document())
```
-->

## Attributes
Attributes are like tag elements represented by classes. Class representing attribute have uppercased first letter and every letter after dash `-` character in original attribute name. 
So for example attribute `accept-charset` has coresponding class name `AcceptCharset`.
Some of attributes are in conflict with Tag element's names. For this situation underscore character `'_'` is appended at the end of attribute class name. Here is table with conflicting names:

| Attribute  | Class      |
:-----------:|:----------:|
| `cite`     | `Cite_`    |
| `data`     | `Data_`    |
| `dir`      | `Dir_`     |
| `form`     | `Form_`    |
| `label`    | `Label_`   |
| `span`     | `Span_`    |
| `style`    | `Style_`   |
| `title`    | `Title_`   |

Attributes can be added into tags right at initialization process. Just add them as constructor parameters.

```python
print(Div(P("First", Class("highlight")), Class("container"), Id("main"), P("Second")))
```
```html
<div class="container" id="main">
  <p class="highlight">
    First
  </p>
  <p>
    Second
  </p>
</div>
```

Another way how to create attribute is to use keyword arguents in tag class constructor. Again replacing dashes `-` to underscore `_` and append underscore after reserved keywords:
| Attribute  | Class      | Keyword argument |
|:----------:|:----------:|:----------------:|
| `class`    | `Class`    | `class_`         |
| `for`      | `For`      | `for_`           |
| `accept-charset`     | `AcceptCharset`    | `accept_charset`    |

```python
print(Form(action="/action_page.php", accept_charset="utf-8"))
```
```html
<form action="/action_page.php" accept-charset="utf-8">
</form>
```

### Styles
For creating inline styles of HTML tag elements you can use `Style_` attribute class.
You can initialize style with raw CSS string in constructor of `Style_` class or you can use keyword named arguments.
```python
sty = Style_(border="2px solid powderblue", margin="50 px", font_size="12 px")

print(P("Styled paragraph", sty))
```
```html
<p style="border: 2px solid powderblue;margin: 50 px;font-size: 12 px;">
  Styled paragraph
</p>
```

### `data-*` attribute
With attribute class `Data_` you can create `data-*` attribute that allow us to store extra information on standard, semantic HTML elements without other hacks such as non-standard attributes, or extra properties on DOM.
```python
data = Data_("hidden-id", "1")
print(Div(data, data_col=5))
```
```html
<div data-col="5" data-hidden-id="1">
</div>
```


## Manipulating objects
### `+` operator
Two tags can be concatenated using `+` operator. Results in parent `Container` tag containing both concatenating tags.
```python
p1 = P("First paragraph")
p2 = P("Second paragraph")

print(p1 + p2)
```
```html
<p>
  First paragraph
</p>
<p>
  Second paragraph
</p>
```

### `add` method
New items into created tags can be added via `add()` method.
- You can add tags, attributes or text into tag.
- Into text nodes you can append another text via `add()` method.
- Adding into attributes you append text in attribute's value.

```python
div = Div()

div.add(P("New paragraph").add(Class('paragraph_class')), Class("div_class"))
print(div)
```
```html
<div class="div_class">
  <p class="paragraph_class">
    New paragraph
  </p>
</div>
```
### `*` operator
Tags can be multiplicated with positive `int` number using `*` multiplication sign. Results in parent `Container` object:
```python
p = P("Paragraph")

print(p * 3)
```
```html
<p>
  Paragraph
</p>
<p>
  Paragraph
</p>
<p>
  Paragraph
</p>
```

### `list` notation
Child nodes of the tag can be accesed through python list notation:
```python
div = Div(P("First paragraph"), Br(), P('Second paragraph class'))

div[2] = Strong('strong text')

del div[1]

print(div)
```
```html
<div>
  <p>
    First paragraph
  </p>
  <strong>
    strong text
  </strong>
</div>
```
### `dict` notation
Attributes can be accesed, modified or deleted from tag object through dictionary notation:
```python
div = Div(Class("container"), Id("main"))

del div['id']
div['class'] = "new_container"
print(div)
```
```html
<div class="new_container">
</div>
```

### `find` method
HTML elements can be searched inside another using `find` method:
```python
div = Div(
      P("Foo bar baz"),
      Img(Src("img.png")),
      Id("foo"),
      Ol(Class("bar"),
      *[Li(i) for i in range(10)]),
      Em("bar"),
      Div(Id("inner_div")))

div.find(Div()) # Finds all divs in div (including self)
# return 2 divs: [<:: Div element: 4 child nodes, 1 attributes ::>, <:: Div element: no childs, 1 attributes ::>]

div.find(Div(Id("inner_div"))) # Finds all divs with id="inner_div"
# return 1 div: [<:: Div element: no childs, 1 attributes ::>]

div.find(Li(1)) # Finds all li with text "1"
# return 1 li: [<:: Li element: 1 child nodes ::>]

div.find("bar") # Finds all Text nodes containing 'bar'
# return 2 Text nodes: [<:: Text: "Foo bar ba..." ::>, <:: Text: "bar" ::>]
```

## Context manager
Tags and attributes can be created using context manager. Just use `with` keyword. You can even nest `with` statements.
```python
div: HtmlElement = None
with Div(H1("Header")) as div, P() as p:
    with Span() as sp, Strong():
        Text("foo")
        Text("bar")

        sp.add("baz")
        sp[0] = "qux"
    Hr()
print(div)

```
```html
<div>
  <h1>
    Header
  </h1>
  <p>
    <span>
      qux
      <strong>
        foo
        bar
      </strong>
    </span>
    <hr>
  </p>
</div>
```

<!---
TODO
- Aria-
-->



