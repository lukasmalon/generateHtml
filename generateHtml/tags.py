from __future__ import annotations
from enum import Enum
from copy import deepcopy

from generateHtml.context import ContextStack as ContextElement
from generateHtml.attributes import (
    HtmlAttribute,
    DashedHtmlAttribute,
    _UNDERSCORED_ATTRIBUTES,
    _DASHED_ATTRIBUTES,
)
from generateHtml.exceptions import (
    DuplicateAttributeError,
    WrongAttributeElementCombinationError,
    IllegalCompositionError,
)

from generateHtml.utils import check_max_occurences, get_class_from_string, escape_html


class HtmlElement(ContextElement):
    """Base class containing properties used in all html element tags.
    """
    def __init__(self, *inner_content, **attributes):
        super().__init__()
        self._child_nodes: list[HtmlElement | Text] = []
        self._attributes: dict[str, HtmlAttribute] = {}

        self._parse_attributes(attributes)
        self._parse_inner_content(inner_content)

        self._validate_attributes()

    def _parse_attributes(self, attributes: dict[str, HtmlAttribute | str]) -> None:
        for key, val in attributes.items():
            # Convert kwargs attribute name into dict value (as original HTML)
            attribute_key: str = key.lower().strip("_").replace("_", "-")
            if isinstance(val, HtmlAttribute):
                self.attributes[attribute_key] = val
            elif isinstance(val, str):
                # Convert kwargs attribute name into class name
                splitted: list[str] = attribute_key.split("-", 1)
                dashed_part: str | None = (
                    splitted[1]
                    if len(splitted) > 1 and splitted[0] in _DASHED_ATTRIBUTES
                    else ""
                )

                underscoring_collision = (
                    "_"
                    if attribute_key.partition("-")[0] in _UNDERSCORED_ATTRIBUTES
                    else ""
                )

                attribute_class: str = ''.join((a.capitalize() for a in attribute_key.split('-')))
                attribute_class = (
                    f"{attribute_class}{underscoring_collision}"
                )
                # Use key to find HtmlAttribute class and then initialize it with val as argument
                attribute_class_ = get_class_from_string("generateHtml.attributes", attribute_class)
                self.attributes[attribute_key] = (
                    attribute_class_(dashed_part, val)
                    if issubclass(attribute_class_, DashedHtmlAttribute)
                    else attribute_class_(val)
                )
            else:
                raise ValueError(
                    f"Value {val} for the key {key} has to be str or HtmlAttribute. Got '{type(val)}'"
                )

    def _parse_inner_content(self, inner_content, index: int|None = None) -> None:
        """Method to extract HTML child nodes and HTML node attributes from iterable item."""
        if index is not None and isinstance(index, int) and len(self) < index:
            raise IndexError("Out of range while inserting into child list.")

        for attr in inner_content:
            if self is attr:  # Preventing circular dependency
                attr = deepcopy(attr)
            if isinstance(attr, object) and issubclass(type(attr), HtmlAttribute):
                self.attributes[attr.name_to_string()] = attr
                self._validate_attributes()
                self._remove_from_context(attr)
            elif isinstance(attr, object) and issubclass(type(attr), HtmlElement):
                if index:
                    self.child_nodes.insert(index, attr)
                    index += 1
                else:
                    self.child_nodes.append(attr)
            elif isinstance(attr, (Text, str, int, float)):
                text_node = Text(str(attr)) if not isinstance(attr, Text) else attr
                if index:
                    self.child_nodes.insert(index, attr)
                    index += 1
                else:
                    self.child_nodes.append(text_node)
            elif isinstance(attr, (list, tuple)):
                # recursive parsing of elements in iterables
                self._parse_inner_content(attr, index)
            else:
                raise TypeError(
                    f"Argument {attr} is not subclass of {HtmlAttribute}, "
                    f"nor subclass of {HtmlElement} nor str"
                )

        # Removing nodes which have parent from context
        if issubclass(type(self), ContextElement):
            for child in self.child_nodes:                
                self._remove_from_context(child)

    def _validate_attributes(self):
        # Check for attribute duplicates
        duplicate_attr = check_max_occurences(
            (
                attribute
                for attribute in self.attributes.values()
                if not issubclass(type(attribute), DashedHtmlAttribute)
            ),
            1,
        )
        if duplicate_attr:
            raise DuplicateAttributeError(
                f"Attribute {duplicate_attr[0]} occured in tag more than once: {duplicate_attr[1]} times."
            )

        # TODO: Check for attribute combination in tag

        # Check assignment attributes to parent html tags
        for attr in self.attributes.values():
            parent_tags = getattr(attr, "parent_tags", None)
            if parent_tags is not None and self.__class__.__name__ not in parent_tags:
                raise WrongAttributeElementCombinationError(
                    f"Attribute '{attr.__class__.__name__}' "
                    f"cannot be used in tag '{self.__class__.__name__}'. Try one of these tags instead: {', '.join(parent_tags)}"
                )

    def _display_prepare(
        self,
        pretty: bool = False,
        new_line: str = "\n",
        indent: str = "  ",
        depth_level: int = 0,
    ) -> str:
        class_name = getattr(
            self.__class__, "display_name", self.__class__.__name__.lower()
        )
        new_line = new_line if pretty else ""
        indent = indent if pretty else ""
        attribute_space = " " if self.attributes else ""

        return (
            f"{''.join([new_line if depth_level else '', depth_level*indent])}"
            f"<{class_name}{attribute_space}"
            f"{' '.join((attr._display_prepare() for key, attr in self.attributes.items()))}>"
            f"{''.join((child._display_prepare(pretty, new_line, indent, depth_level+1) for child in self.child_nodes))}"
            f"{''.join([new_line, depth_level*indent, f'</{class_name}>']) if not issubclass(type(self), SelfClosingElement) else ''}"
        )

    def display(
        self, pretty: bool = True, new_line: str = "\n", indent: str = "  "
    ) -> str:
        """Main function for displaying element's content.

        Args:
            pretty (bool, optional): If set to True, it will display the entire element including attributes and children with indentation.
                                     If set to False, entire element will be displayed on one line with minimum whitespaces. Defaults to True.
            new_line (str, optional): Optional to change used newline character. Defaults to '\n'.
            indent (str, optional): Optional to change indentation character. Defaults to '  '.

        Returns:
            str: String representation of the element structure.
        """
        return self._display_prepare(pretty, new_line, indent, 0)

    def __str__(self) -> str:
        return self.display()

    def __repr__(self) -> str:
        return (
            f"<:: {self.__class__.__name__} element: {f'{len(self.child_nodes)} child nodes' if self.child_nodes else 'no childs'}"
            f"{f', {len(self.attributes)} attributes' if self.attributes else ''} ::>"
        )

    def __getitem__(self, key):
        if isinstance(key, str):
            # Convert kwargs attribute name into dict value (as original HTML)
            attribute_key: str = key.lower().strip("-").replace("_", "-")

            val = self.attributes.get(attribute_key)
            if val is None:
                raise KeyError(f"Attribute: '{attribute_key}' does not exist in element.")
            return val
        elif isinstance(key, int):
            return self.child_nodes[key]
        elif isinstance(key, slice):
            return self.child_nodes[key]
        else:
            raise KeyError(f"Invalid key type: {key}")

    def __setitem__(self, key, value):
        if isinstance(key, str):
            self._parse_attributes({key: value})
            self._validate_attributes()
        elif isinstance(key, int):
            if len(self) < key:
                raise IndexError("Out of range while inserting into child list.")
            if issubclass(type(value), HtmlAttribute):
                raise TypeError('Cannot add attribute into child elements.')
            elif issubclass(type(value), (Text, int, float, str)):
                value = Text(str(value)) if not isinstance(value, Text) else value
            else:
                value = Container(value)
            self.add(value, index=key)

        elif isinstance(key, slice):
            #TODO: Slice adding
            raise NotImplementedError("Adding new items through slice notation is not implemented yet")
        else:
            raise KeyError(f"Wrong key type {type(key)}. Try int for accesing elemnt's children or str for attributes.")
        

    def __delitem__(self, key):
        if isinstance(key, str):
            # Convert kwargs attribute name into dict value (as original HTML)
            attribute_key: str = key.lower().strip("-").replace("_", "-")

            val = self.attributes.get(attribute_key)
            if val:
                del self.attributes[attribute_key]
            else:
                raise KeyError(f"Attribute: '{attribute_key}' does not exist in element.")
        elif isinstance(key, int):
            if len(self) < key:
                raise IndexError(f"Index '{key}' out of range in child nodes.")
            del self.child_nodes[key]
        elif isinstance(key, slice):
            del self.child_nodes[key]
        else:
            raise KeyError(f"Invalid key type: {key}")

    def __len__(self):
        return len(self.child_nodes)

    def __add__(self, other):
        if isinstance(other, HtmlElement):
            return Container(self, other)
        elif isinstance(other, (HtmlAttribute, Text, str, float, int)):
            self.add(other)
            return self
        else:
            raise TypeError(f"canot merge '{type(self)}' of type '{type(other)}'")

    def __radd__(self, other):
        if isinstance(other, HtmlElement):
            return Container(other, self)
        elif isinstance(other, (HtmlAttribute)):
            self.add(other)
            return self
        elif isinstance(other, (Text, str, float, int)):
            return Container(other, self)
        else:
            raise TypeError(f"canot merge '{type(self)}' of type '{type(other)}'")

    def __mul__(self, other: int):
        if not isinstance(other, int):
            raise TypeError(
                f"can't multiply sequence by non-int of type '{type(other)}'"
            )
        if other < 0:
            raise ValueError(
                f"can't multiply sequence by negative values: '{other}'"
            )
        new_container = Container()
        for _ in range(other):
            new_container.add(self)
        return new_container

    def add(self, *new_child: HtmlElement | HtmlAttribute | Text | int | str | float, index: int|None = None):
        """Main method for adding new attributes, child html elements or text nodes into existing objects"""
        self._parse_inner_content(new_child, index)

        return self

    @property
    def child_nodes(self) -> list[HtmlElement | Text]:
        return self._child_nodes

    @property
    def attributes(self) -> dict[str, HtmlAttribute]:
        return self._attributes


class SelfClosingElement(HtmlElement):
    def __init__(self, *attributes, **kwgs_attributes):
        super().__init__(*attributes, **kwgs_attributes)

        if self.child_nodes:
            raise IllegalCompositionError(
                f"Self closing element '{self.__class__.__name__}' cannot contain inner content."
            )


class Text(ContextElement):
    def __init__(self, text: Text | int | str | float | None):
        super().__init__()
        if isinstance(text, Text):
            text = text.value
        elif isinstance(text, (int, float, str)):
            text = str(text)
        elif text is None:
            text = ''
        else:
            raise TypeError(f'Unsupported type for Text node value: {type(text)}')
        self.value: str = escape_html(text)

    def add(self, *new_child: Text | int | str | float):
        """Method for appending text in text node"""
        for child in new_child:
            if not isinstance(child, (Text | int | str | float)):
                raise TypeError(
                    f"Into class {self.__class__.__name__} you can only add another text!"
                )

            self.value += child.value if isinstance(child, Text) else escape_html(str(child))
        return self

    def __len__(self) -> int:
        return self.value.__len__()

    def __iter__(self) -> int:
        return self.value.__iter__()

    def __str__(self) -> str:
        return self.value

    def __repr__(self) -> str:
        return f'<:: {self.__class__.__name__}: "{self.value[:10]}{"..." if len(self.value) > 10 else ""}" ::>'

    def _display_prepare(
        self,
        pretty: bool = False,
        new_line: str = "\n",
        indent: str = "  ",
        depth_level: int = 0,
    ) -> str:
        new_line = new_line if pretty else ""
        indent = indent if pretty else ""

        return f"{new_line if depth_level else ''}{depth_level*indent if depth_level else ''}{self.value}" if pretty else self.value


class Container(HtmlElement):
    """Class for storing elements. Does not have open/closing tags. Displays only child elements."""

    def __init__(self, *inner_content):
        super().__init__(*inner_content)
        if self.attributes:
            raise IllegalCompositionError(
                f"{self.__class__.__name__} cannot contain attributes."
            )

    def _display_prepare(
        self,
        pretty: bool = False,
        new_line: str = "\n",
        indent: str = "  ",
        depth_level: int = 0,
    ) -> str:
        new_line = new_line if pretty else ""
        indent = indent if pretty else ""

        return (
            f"{''.join([depth_level*indent])}"
            f"{''.join((child._display_prepare(pretty, new_line, indent, depth_level) for child in self.child_nodes))}"
            f"{''.join([depth_level*indent])}"
        )


    def add(self, *new_child: HtmlElement | Text | int | str | float, index: int|None = None):
        """Main method for adding new attributes, child html elements or text nodes into existing objects"""
        self._parse_inner_content(new_child, index=index)
        if self.attributes:
            raise IllegalCompositionError(
                f"{self.__class__.__name__} cannot contain attributes."
            )

        return self


class Document(Container):
    """Document container prepared with basic HTML structure.
       Add function adds everything into document's body element.
       Enables accessing into head and body properties.

    Args:
        Container (_type_): _description_
    """

    def __init__(self, *inner_content, **attributes):
        super().__init__()
        self._head = Head(Meta(charset="utf-8"), Title("Title of the page"))
        self._body = Body(*inner_content, **attributes)
        self._child_nodes = Container(Doctype(), Html(self.head, self.body))

    @property
    def head(self):
        return self._head

    @property
    def body(self):
        return self._body

    def add(self, *new_child: HtmlElement | Text | int | str | float, index: int | None = None):
        """Main method for adding new attributes, child html elements or text nodes into existing objects"""
        self.body._parse_inner_content(new_child, index)

        if self.attributes:
            raise IllegalCompositionError(
                f"{self.__class__.__name__} cannot contain attributes."
            )

        return self


### HTML Elements according to https://www.w3schools.com/tags/ref_byfunc.asp sorted by category
## Basic HTML


class DoctypeDeclaration(Enum):
    HTML5 = "!DOCTYPE HTML"
    HTML4_01_STRICT = '!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN"\n"http://www.w3.org/TR/html4/strict.dtd"'
    HTML4_01_TRANSITIONAL = '!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN"\n"http://www.w3.org/TR/html4/loose.dtd"'
    HTML4_01_FRAMESET = '!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Frameset//EN"\n"http://www.w3.org/TR/html4/frameset.dtd"'
    XHTML1_0_STRICT = '!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"\n"http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd"'
    XHTML1_0_TRANSITIONAL = '!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"\n"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd"'
    XHTML1_0_FRAMESET = '!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Frameset//EN"\n"http://www.w3.org/TR/xhtml1/DTD/xhtml1-frameset.dtd"'
    XHTML1_1 = '!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN"\n"http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd"'
    XHTML1_1_BASIC = '!DOCTYPE html PUBLIC "-//W3C//DTD XHTML Basic 1.1//EN"\n"http://www.w3.org/TR/xhtml-basic/xhtml-basic11.dtd"'


class Doctype(SelfClosingElement):
    """Defines the document type."""

    display_name: str = "!DOCTYPE html"

    def __init__(
        self,
        *attributes,
        declaration: DoctypeDeclaration = DoctypeDeclaration.HTML5,
        **kwgs_attributes,
    ):
        super().__init__(*attributes, **kwgs_attributes)
        self.__class__.display_name = declaration.value


class Html(HtmlElement):
    """Defines an HTML document."""


class Head(HtmlElement):
    """Contains metadata/information for the document."""


class Title(HtmlElement):
    """Defines a title for the document."""


class Body(HtmlElement):
    """Defines the document's body."""


class H1(HtmlElement):
    """Defines HTML H1 heading."""


class H2(HtmlElement):
    """Defines HTML H2 heading."""


class H3(HtmlElement):
    """Defines HTML H3 heading."""


class H4(HtmlElement):
    """Defines HTML H4 heading."""


class H5(HtmlElement):
    """Defines HTML H5 heading."""


class H6(HtmlElement):
    """Defines HTML H6 heading."""


class Paragraph(HtmlElement):
    """Defines a paragraph. Alias to 'P' class."""

    display_name: str = "p"


class P(HtmlElement):
    """Defines a paragraph. Alias to 'Paragraph' class."""


class Br(SelfClosingElement):
    """Inserts a single line break."""


class Hr(SelfClosingElement):
    """Defines a thematic change in the content."""


class Comment(HtmlElement):
    """Class defining comment element."""

    def __init__(self, *inner_content, condition: str = "", **kwargs):
        super().__init__(*inner_content, **kwargs)
        self._condition = condition

    def _display_prepare(
        self,
        pretty: bool = False,
        new_line: str = "\n",
        indent: str = "  ",
        depth_level: int = 0,
    ) -> str:
        new_line = new_line if pretty and self.child_nodes else ""
        indent = indent if pretty else ""
        attribute_space = " " if self.attributes else ""

        start_condition = f"<!--[if {self._condition}]>" if self._condition else '<!--'
        end_condition = '<![endif]-->' if self._condition else '-->'
        return (
            f"{''.join((new_line, depth_level*indent)) if depth_level else ''}"
            f"{start_condition}{attribute_space}{' '.join((attr._display_prepare() for key, attr in self.attributes))}"
            f"{''.join((child._display_prepare(pretty, new_line, indent, depth_level+1) for child in self.child_nodes))}"
            f"{new_line + (depth_level*indent) + end_condition}"
            f"{new_line if depth_level and not self.child_nodes else ''}"
        )


## Formatting
class Acronym(HtmlElement):
    """Not supported in HTML5. Use <abbr> instead.
    Defines an acronym."""


class Abbr(HtmlElement):
    """Defines an abbreviation or an acronym."""


class Address(HtmlElement):
    """Defines contact information for the author/owner of a document/article."""


class B(HtmlElement):
    """Defines bold text."""


class Bdi(HtmlElement):
    """Isolates a part of text that might be formatted in a different direction from other text outside it."""


class Bdo(HtmlElement):
    """Overrides the current text direction."""


class Big(HtmlElement):
    """Not supported in HTML5. Use CSS instead.
    Defines big text."""


class Blockquote(HtmlElement):
    """Defines a section that is quoted from another source"""


class Center(HtmlElement):
    """Not supported in HTML5. Use CSS instead.
    Defines centered text."""


class Cite(HtmlElement):
    """Defines the title of a work."""


class Code(HtmlElement):
    """Defines a piece of computer code."""


class Del(HtmlElement):
    """Defines text that has been deleted from a document."""


class Dfn(HtmlElement):
    """Specifies a term that is going to be defined within the content."""


class Em(HtmlElement):
    """Defines emphasized text."""


class Font(HtmlElement):
    """Not supported in HTML5. Use CSS instead.
    Defines font, color, and size for text."""


class I(HtmlElement):
    """Defines a part of text in an alternate voice or mood."""


class Ins(HtmlElement):
    """Defines a text that has been inserted into a document."""


class Kbd(HtmlElement):
    """Defines keyboard input."""


class Mark(HtmlElement):
    """Defines marked/highlighted text."""


class Meter(HtmlElement):
    """Defines a scalar measurement within a known range (a gauge)."""


class Pre(HtmlElement):
    """Defines preformatted text."""


class Progress(HtmlElement):
    """Represents the progress of a task."""


class Q(HtmlElement):
    """Defines a short quotation."""


class Rp(HtmlElement):
    """Defines what to show in browsers that do not support ruby annotations."""


class Rt(HtmlElement):
    """Defines an explanation/pronunciation of characters (for East Asian typography)."""


class Ruby(HtmlElement):
    """Defines a ruby annotation (for East Asian typography)."""


class S(HtmlElement):
    """Defines text that is no longer correct."""


class Samp(HtmlElement):
    """Defines sample output from a computer program."""


class Small(HtmlElement):
    """Defines smaller text."""


class Strike(HtmlElement):
    """Not supported in HTML5. Use <del> or <s> instead.
    Defines strikethrough text."""


class Strong(HtmlElement):
    """Defines important text."""


class Sub(HtmlElement):
    """Defines subscripted text."""


class Sup(HtmlElement):
    """Defines superscripted text."""


class Template(HtmlElement):
    """Defines a container for content that should be hidden when the page loads."""


class Time(HtmlElement):
    """Defines a specific time (or datetime)."""


class Tt(HtmlElement):
    """Not supported in HTML5. Use CSS instead.
    Defines teletype text."""


class U(HtmlElement):
    """Defines some text that is unarticulated and styled differently from normal text."""


class Var(HtmlElement):
    """Defines a variable."""


class Wbr(SelfClosingElement):
    """Defines a possible line-break."""


## Forms and Input
class Form(HtmlElement):
    """Defines an HTML form for user input."""


class Input(SelfClosingElement):
    """Defines an input control."""


class Textarea(HtmlElement):
    """Defines a multiline input control (text area)."""


class Button(HtmlElement):
    """Defines a clickable button."""


class Select(HtmlElement):
    """Defines a drop-down list."""


class Optgroup(HtmlElement):
    """Defines a group of related options in a drop-down list."""


class Option(HtmlElement):
    """Defines an option in a drop-down list."""


class Label(HtmlElement):
    """Defines a label for an <input> element."""


class Fieldset(HtmlElement):
    """Groups related elements in a form."""


class Legend(HtmlElement):
    """Defines a caption for a <fieldset> element."""


class Datalist(HtmlElement):
    """Specifies a list of pre-defined options for input controls."""


class Output(HtmlElement):
    """Defines the result of a calculation."""


## Frames
class Frame(HtmlElement):
    """Not supported in HTML5.
    Defines a window (a frame) in a frameset."""


class Frameset(HtmlElement):
    """Not supported in HTML5.
    Defines a set of frames."""


class Noframes(HtmlElement):
    """Not supported in HTML5.
    Defines an alternate content for users that do not support frames."""


class Iframe(HtmlElement):
    """Defines an inline frame."""


## Images
class Img(SelfClosingElement):
    """Defines an image."""


class Map(HtmlElement):
    """Defines a client-side image map."""


class Area(SelfClosingElement):
    """Defines an area inside an image map."""


class Canvas(HtmlElement):
    """Used to draw graphics, on the fly, via scripting (usually JavaScript)."""


class Figcaption(HtmlElement):
    """Defines a caption for a <figure> element."""


class Figure(HtmlElement):
    """Specifies self-contained content."""


class Picture(HtmlElement):
    """Defines a container for multiple image resources."""


class Svg(HtmlElement):
    """Defines a container for SVG graphics."""


## Audio / Video
class Audio(HtmlElement):
    """Defines sound content."""


class Source(SelfClosingElement):
    """Defines multiple media resources for media elements (<video>, <audio> and <picture>)."""


class Track(SelfClosingElement):
    """Defines text tracks for media elements (<video> and <audio>)."""


class Video(HtmlElement):
    """Defines a video or movie."""


## Links
class A(HtmlElement):
    """Defines a hyperlink."""


class Link(SelfClosingElement):
    """Defines the relationship between a document and an external resource (most used to link to style sheets)."""


class Nav(HtmlElement):
    """Defines navigation links."""


## Lists
class Menu(HtmlElement):
    """Defines an alternative unordered list."""


class Ul(HtmlElement):
    """Defines an unordered list."""


class Ol(HtmlElement):
    """Defines an ordered list."""


class Li(HtmlElement):
    """Defines a list item."""


class Dir(HtmlElement):
    """Not supported in HTML5. Use <ul> instead.
    Defines a directory list."""


class Dl(HtmlElement):
    """Defines a description list."""


class Dt(HtmlElement):
    """Defines a term/name in a description list"""


class Dd(HtmlElement):
    """Defines a description of a term/name in a description list"""


## Tables
class TableOption(Enum):
    HEADER = "header"


class HeaderOption(Enum):
    ROW = "row"
    COLUMN = "column"
    BOTH = "both"


class Caption(HtmlElement):
    """Defines a table caption."""


class Td(HtmlElement):
    """Defines a cell in a table."""


class Tr(HtmlElement):
    """Defines a row in a table."""


class Th(HtmlElement):
    """Defines a header cell in a table."""


class Tfoot(HtmlElement):
    """Groups the footer content in a table."""


class Tbody(HtmlElement):
    """Groups the body content in a table."""


class Thead(HtmlElement):
    """Groups the header content in a table."""


class Col(SelfClosingElement):
    """Specifies column properties for each column within a <colgroup> element."""


class Colgroup(HtmlElement):
    """Specifies a group of one or more columns in a table for formatting."""


class Table(HtmlElement):
    """Class defining table element."""

    @staticmethod
    def check_table_content(content, options: dict[TableOption, HeaderOption] = {}):
        header = options.get(TableOption.HEADER.value, None)

        tagged_content = list()
        for row_idx, row in enumerate(content):
            if isinstance(row, (list, tuple)):
                item_row = list()
                for col_idx, item in enumerate(row):
                    if isinstance(item, (Text, str, int, float)):
                        if header is not None and (
                            (
                                col_idx == 0
                                and header
                                in (HeaderOption.BOTH.value, HeaderOption.COLUMN.value)
                            )
                            or (
                                row_idx == 0
                                and header
                                in (HeaderOption.BOTH.value, HeaderOption.ROW.value)
                            )
                        ):
                            item_row.append(Th(item))
                        else:
                            item_row.append(Td(item))
                    elif isinstance(item, (HtmlElement)):
                        if header is not None and (
                            (
                                col_idx == 0
                                and header
                                in (HeaderOption.BOTH.value, HeaderOption.COLUMN.value)
                            )
                            or (
                                row_idx == 0
                                and header
                                in (HeaderOption.BOTH.value, HeaderOption.ROW.value)
                            )
                        ):
                            item_row.append(Th(item))
                        else:
                            item_row.append(item)
                tagged_content.append(Tr(item_row))
        return tagged_content

    def __init__(
        self,
        *attributes,
        content: list[list] = list(),
        options: dict[TableOption, HeaderOption] = {},
        **kwargs,
    ):
        super().__init__(*attributes, **kwargs)
        tagged_content = self.check_table_content(content, options)
        self._child_nodes = tagged_content if tagged_content else self._child_nodes


## Styles and Semantics
class Style(HtmlElement):
    """Defines style information for a document."""


class Div(HtmlElement):
    """Defines a section in a document."""


class Span(HtmlElement):
    """Defines a section in a document."""


class Header(HtmlElement):
    """Defines a header for a document or section."""


class Hgroup(HtmlElement):
    """Defines a header and related content."""


class Footer(HtmlElement):
    """Class defining footer document element."""


class Main(HtmlElement):
    """Specifies the main content of a document."""


class Section(HtmlElement):
    """Defines a section in a document."""


class Search(HtmlElement):
    """Defines a search section."""


class Article(HtmlElement):
    """Defines an article."""


class Aside(HtmlElement):
    """Defines content aside from the page content."""


class Details(HtmlElement):
    """Defines additional details that the user can view or hide."""


class Dialog(HtmlElement):
    """Defines a dialog box or window."""


class Summary(HtmlElement):
    """Defines a visible heading for a <details> element."""


class Data(HtmlElement):
    """Adds a machine-readable translation of a given content."""


## Meta Info
class Meta(SelfClosingElement):
    """Defines metadata about an HTML document."""


class Base(SelfClosingElement):
    """Specifies the base URL/target for all relative URLs in a document."""


class Basefont(HtmlElement):
    """Not supported in HTML5. Use CSS instead.
    Specifies a default color, size, and font for all text in a document."""


## Programming
class Script(HtmlElement):
    """Defines a client-side script."""


class Noscript(HtmlElement):
    """Defines an alternate content for users that do not support client-side scripts."""


class Applet(HtmlElement):
    """Not supported in HTML5. Use <embed> or <object> instead.
    Defines an embedded applet."""


class Embed(SelfClosingElement):
    """Defines a container for an external (non-HTML) application."""


class Object(HtmlElement):
    """Defines an embedded object."""


class Param(HtmlElement):
    """Defines a parameter for an object."""
