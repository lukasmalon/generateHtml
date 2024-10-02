from __future__ import annotations
from enum import Enum

from context import ContextStack as ContextElement
from utils import prepend_dash_before_uppercase, escape_html

## Using underscore after attribute name for attribute's class
UNDERSCORED_ATTRIBUTES = ('data', 'form', 'label', 'cite', 'dir', 'style', 'title', 'span', 'aria')
DASHED_ATTRIBUTES = ('data', 'aria')

class HtmlAttribute(ContextElement):

    @classmethod
    def name_to_string(cls:HtmlAttribute) -> str:
        """Converts class name into original attribute format.

        Parameters
        ----------
        cls : HtmlAttribute
           HtmlAttribute class for converting. 

        Returns
        -------
        str
            Original attribute format in string.
        """
        return prepend_dash_before_uppercase(cls.__name__).lower().replace('_', '-').strip('-')

    @staticmethod
    def check_attribute_value(value) -> str:
        if not (isinstance(value, (float, int, str))):
            raise TypeError(f"Wrong data type used for attribute {__class__.__name__}: "\
                                    f"Got {type(value)} expected str.")        
        return str(value)

    def __init__(self, value: float|int|str):
        super().__init__()
        self._value = escape_html(self.check_attribute_value(value))

    def _display_prepare(self) -> str:
        class_name = getattr(self.__class__, 'display_name', self.__class__.__name__.lower())
        return f'{class_name}="{self._value}"'

    def display(self) -> str:
        return self._display_prepare()

    def __str__(self) -> str:
        return self.display()

    def add(self, *values):
        for val in values:
            if isinstance(val, (int, float, str)):
                self.value += escape_html(str(val))
            else:
                raise ValueError("In attribute can only be added text.")
        return self

    @property
    def name(self):
        return getattr(self.__class__, 'display_name', self.__class__.__name__.lower())

    @property
    def value(self) -> str:
        return self._value

    @value.setter
    def value(self, value: float|int|str):
        self._value = value

class BooleanTrueDisplayOption(Enum):
    SHORT       = 'short'
    EMPTY       = 'empty'
    REPEATED    = 'repeated'

class BooleanHtmlAttribute(HtmlAttribute):
    """Defines attribute with boolean value. Displays only attribute's key without value."""
    def __init__(self, value: float|int|str="", true_value: str|BooleanTrueDisplayOption='short'):
        super().__init__(value)
        self._value = escape_html(self.check_attribute_value(value))
        self.true_value_display = true_value

    def _display_prepare(self, true_value: None|str|BooleanTrueDisplayOption = None):
        class_name = getattr(self.__class__, 'display_name', self.__class__.__name__.lower())
        if true_value is None:
            true_value = self.true_value_display
        elif isinstance(true_value, str):
            try:
                true_value = BooleanTrueDisplayOption(true_value.lower())
            except ValueError:
                pass
        if true_value == BooleanTrueDisplayOption.SHORT:
            return f'{class_name}'
        elif true_value == BooleanTrueDisplayOption.EMPTY:
            return f'{class_name}=""'
        elif true_value == BooleanTrueDisplayOption.REPEATED:
            return f'{class_name}="{class_name}"'
        elif isinstance(true_value, str):
            return f'{class_name}="{true_value}"'
        else:
            raise ValueError(f"Unsupported true_value: {true_value}")
        return f'{class_name}'

class MultipleValueHtmlAttribute(HtmlAttribute):
    """Defines attribute with multiple value separated with selected separator."""
    def __init__(self, value: str, *other_values, separator: str = " "):
        super().__init__(value)

        for val in other_values:
            self.value = ''.join([self.value, separator, \
                escape_html(self.check_attribute_value(val))])

class DashedHtmlAttribute(HtmlAttribute):
    def __init__(self, after_dash_part: str, value: float|int|str):
        super().__init__(value)
        self._after_dash_part: str = after_dash_part

    def _display_prepare(self) -> str:
        return f'{self.name}="{self._value}"'

    @property
    def name(self) -> str:
        class_name = getattr(self.__class__, 'display_name', self.__class__.__name__.lower())
        return f"{class_name}{'-' if self._after_dash_part else ''}{self._after_dash_part}"

class Data_(DashedHtmlAttribute):
    """Specifies the URL of the resource to be used by the object"""
    display_name: str = 'data'

class Aria_(DashedHtmlAttribute):
    """Accessible Rich Internet Applications (ARIA) is a set of roles and attributes that define ways to
    make web content and web applications (especially those developed with JavaScript) more accessible 
    to people with disabilities."""
    display_name: str = 'aria'

class Style_(HtmlAttribute):
    """Specifies an inline CSS style for an element"""
    display_name: str = 'style'

    def __init__(self, *styles: str, **kwgs_styles):
        super().__init__(value='')
        sty :str = ''
        for val in styles:
            sty += val
        for key, val in kwgs_styles.items():
            sty += f"{key.replace('_', '-')}: {val};"
        self.value += sty

class Accept(HtmlAttribute):
    """Specifies the types of files that the server accepts (only for type="file")"""
    parent_tags = frozenset(('Input',))

class AcceptCharset(HtmlAttribute):
    """Specifies the character encodings that are to be used for the form 
    submission"""
    parent_tags = frozenset(('Form',))

class Accesskey(HtmlAttribute):
    """Specifies a shortcut key to activate/focus an element"""

class Action(HtmlAttribute):
    """Specifies where to send the form-data when a form is submitted"""
    parent_tags = frozenset(('Form',))

class Alt(HtmlAttribute):
    """Specifies an alternate text when the original element fails to display"""
    parent_tags = frozenset(('Area', 'Img', 'Input'))

class Async(BooleanHtmlAttribute):
    """Specifies that the script is executed asynchronously (only for external 
    scripts)"""
    parent_tags = frozenset(('Script',))

class Autocomplete(HtmlAttribute):
    """Specifies whether the <form> or the <input> element should have autocomplete 
    enabled"""
    parent_tags = frozenset(('Form', 'Input'))

class Autofocus(BooleanHtmlAttribute):
    """Specifies that the element should automatically get focus when the page 
    loads"""
    parent_tags = frozenset(('Button', 'Input', 'Select', 'Textarea'))

class Autoplay(BooleanHtmlAttribute):
    """Specifies that the audio/video will start playing as soon as it is ready"""
    parent_tags = frozenset(('Audio', 'Video'))

class Charset(HtmlAttribute):
    """Specifies the character encoding"""
    parent_tags = frozenset(('Meta', 'Script'))

class Checked(BooleanHtmlAttribute):
    """Specifies that an <input> element should be pre-selected when the page loads 
    (for type="checkbox" or type="radio")"""
    parent_tags = frozenset(('Input',))

class Cite_(HtmlAttribute):
    """Specifies a URL which explains the quote/deleted/inserted text"""
    display_name: str = 'cite'
    parent_tags = frozenset(('Del', 'Ins'))

class Class(MultipleValueHtmlAttribute):
    """Specifies one or more class names for an element (refers to a class in a 
    style sheet)"""

class Cols(HtmlAttribute):
    """Specifies the visible width of a text area"""
    parent_tags = frozenset(('Textarea',))

class Colspan(HtmlAttribute):
    """Specifies the number of columns a table cell should span"""
    parent_tags = frozenset(('Td', 'Th'))

class Content(HtmlAttribute):
    """Gives the value associated with the http-equiv or name attribute"""
    parent_tags = frozenset(('Meta',))

class Contenteditable(HtmlAttribute):
    """Specifies whether the content of an element is editable or not"""

class Controls(BooleanHtmlAttribute):
    """Specifies that audio/video controls should be displayed (such as a 
    play/pause button etc.)"""
    parent_tags = frozenset(('Audio', 'Video'))

class Coords(HtmlAttribute):
    """Specifies the coordinates of the area"""
    parent_tags = frozenset(('Area',))

class Datetime(HtmlAttribute):
    """Specifies the date and time"""
    parent_tags = frozenset(('Del', 'Ins', 'Time'))

class Default(BooleanHtmlAttribute):
    """Specifies that the track is to be enabled if the user's preferences do not 
    indicate that another track would be more appropriate"""
    parent_tags = frozenset(('Track',))

class Defer(BooleanHtmlAttribute):
    """Specifies that the script is executed when the page has finished parsing 
    (only for external scripts)"""
    parent_tags = frozenset(('Script',))

class Dir_(HtmlAttribute):
    """Specifies the text direction for the content in an element"""
    display_name: str = 'dir'

class Dirname(HtmlAttribute):
    """Specifies that the text direction will be submitted"""
    parent_tags = frozenset(('Input', 'Textarea'))

class Disabled(BooleanHtmlAttribute):
    """Specifies that the specified element/group of elements should be disabled"""
    parent_tags = frozenset(('Button', 'Fieldset', 'Input', 'Option', 'Select', 'Textarea'))

class Download(HtmlAttribute):
    """Specifies that the target will be downloaded when a user clicks on the 
    hyperlink"""
    parent_tags = frozenset(('A', 'Area'))

class Draggable(HtmlAttribute):
    """Specifies whether an element is draggable or not"""

class Enctype(HtmlAttribute):
    """Specifies how the form-data should be encoded when submitting it to the 
    server (only for method="post")"""
    parent_tags = frozenset(('Form',))

class Enterkeyhint(HtmlAttribute):
    """Specifies the text of the enter-key on a virtual keyboard"""

class For(HtmlAttribute):
    """Specifies which form element(s) a label/calculation is bound to"""
    parent_tags = frozenset(('Output',))

class Form_(HtmlAttribute):
    """Specifies the name of the form the element belongs to"""
    display_name: str = 'form'
    parent_tags = frozenset(('Button', 'Fieldset', 'Input', 'Meter', 'Object', 'Output', 'Select', 'Textarea'))

class Formaction(HtmlAttribute):
    """Specifies where to send the form-data when a form is submitted. Only for 
    type="submit" """
    parent_tags = frozenset(('Button', 'Input'))

class Headers(HtmlAttribute):
    """Specifies one or more headers cells a cell is related to"""
    parent_tags = frozenset(('Td', 'Th'))

class Height(HtmlAttribute):
    """Specifies the height of the element"""
    parent_tags = frozenset(('Embed', 'Iframe', 'Img', 'Input', 'Object', 'Video'))

class Hidden(HtmlAttribute):
    """Specifies that an element is not yet, or is no longer, relevant"""

class High(HtmlAttribute):
    """Specifies the range that is considered to be a high value"""
    parent_tags = frozenset(('Meter',))

class Href(HtmlAttribute):
    """Specifies the URL of the page the link goes to"""
    parent_tags = frozenset(('A', 'Area', 'Base', 'Link'))

class Hreflang(HtmlAttribute):
    """Specifies the language of the linked document"""
    parent_tags = frozenset(('A', 'Area', 'Link'))

class HttpEquiv(HtmlAttribute):
    """Provides an HTTP header for the information/value of the content attribute"""
    parent_tags = frozenset(('Meta',))

class Id(HtmlAttribute):
    """Specifies a unique id for an element"""

class Inert(BooleanHtmlAttribute):
    """Specifies that the browser should ignore this section"""

class Inputmode(HtmlAttribute):
    """Specifies the mode of a virtual keyboard"""

class Ismap(BooleanHtmlAttribute):
    """Specifies an image as a server-side image map"""
    parent_tags = frozenset(('Img',))

class Kind(HtmlAttribute):
    """Specifies the kind of text track"""
    parent_tags = frozenset(('Track',))

class Label_(HtmlAttribute):
    """Specifies the title of the text track"""
    display_name: str = 'label'
    parent_tags = frozenset(('Track', 'Option', 'Optgroup'))

class Lang(HtmlAttribute):
    """Specifies the language of the element's content"""

class List(HtmlAttribute):
    """Refers to a <datalist> element that contains pre-defined options for an <input> 
    element"""
    parent_tags = frozenset(('Input',))

class Loop(BooleanHtmlAttribute):
    """Specifies that the audio/video will start over again, every time it is 
    finished"""
    parent_tags = frozenset(('Audio', 'Video'))

class Low(HtmlAttribute):
    """Specifies the range that is considered to be a low value"""
    parent_tags = frozenset(('Meter',))

class Max(HtmlAttribute):
    """Specifies the maximum value"""
    parent_tags = frozenset(('Input', 'Meter', 'Progress'))

class Maxlength(HtmlAttribute):
    """Specifies the maximum number of characters allowed in an element"""
    parent_tags = frozenset(('Input', 'Textarea'))

class Media(HtmlAttribute):
    """Specifies what media/device the linked document is optimized for"""
    parent_tags = frozenset(('A', 'Area', 'Link', 'Source', 'Style'))

class Method(HtmlAttribute):
    """Specifies the HTTP method to use when sending form-data"""
    parent_tags = frozenset(('Form',))

class Min(HtmlAttribute):
    """Specifies a minimum value"""
    parent_tags = frozenset(('Input', 'Meter'))

class Multiple(BooleanHtmlAttribute):
    """Specifies that a user can enter more than one value"""
    parent_tags = frozenset(('Input', 'Select'))

class Muted(BooleanHtmlAttribute):
    """Specifies that the audio output of the video should be muted"""
    parent_tags = frozenset(('Video', 'Audio'))

class Name(HtmlAttribute):
    """Specifies the name of the element"""
    parent_tags = frozenset(('Button', 'Fieldset', 'Form', 'Iframe', 'Input', 'Map', 'Meta', 'Object', 'Output', 'Param', 'Select', 'Textarea'))

class Novalidate(BooleanHtmlAttribute):
    """Specifies that the form should not be validated when submitted"""
    parent_tags = frozenset(('Form',))

class Onabort(HtmlAttribute):
    """Script to be run on abort"""
    parent_tags = frozenset(('Audio', 'Embed', 'Img', 'Object', 'Video'))

class Onafterprint(HtmlAttribute):
    """Script to be run after the document is printed"""
    parent_tags = frozenset(('Body',))

class Onbeforeprint(HtmlAttribute):
    """Script to be run before the document is printed"""
    parent_tags = frozenset(('Body',))

class Onbeforeunload(HtmlAttribute):
    """Script to be run when the document is about to be unloaded"""
    parent_tags = frozenset(('Body',))

class Onblur(HtmlAttribute):
    """Script to be run when the element loses focus"""

class Oncanplay(HtmlAttribute):
    """Script to be run when a file is ready to start playing (when it has buffered 
    enough to begin)"""
    parent_tags = frozenset(('Audio', 'Embed', 'Object', 'Video'))

class Oncanplaythrough(HtmlAttribute):
    """Script to be run when a file can be played all the way to the end without 
    pausing for buffering"""
    parent_tags = frozenset(('Audio', 'Video'))

class Onchange(HtmlAttribute):
    """Script to be run when the value of the element is changed"""

class Onclick(HtmlAttribute):
    """Script to be run when the element is being clicked"""

class Oncontextmenu(HtmlAttribute):
    """Script to be run when a context menu is triggered"""

class Oncopy(HtmlAttribute):
    """Script to be run when the content of the element is being copied"""

class Oncuechange(HtmlAttribute):
    """Script to be run when the cue changes in a """
    parent_tags = frozenset(('Track',))

class Oncut(HtmlAttribute):
    """Script to be run when the content of the element is being cut"""

class Ondblclick(HtmlAttribute):
    """Script to be run when the element is being double-clicked"""

class Ondrag(HtmlAttribute):
    """Script to be run when the element is being dragged"""

class Ondragend(HtmlAttribute):
    """Script to be run at the end of a drag operation"""

class Ondragenter(HtmlAttribute):
    """Script to be run when an element has been dragged to a valid drop target"""

class Ondragleave(HtmlAttribute):
    """Script to be run when an element leaves a valid drop target"""

class Ondragover(HtmlAttribute):
    """Script to be run when an element is being dragged over a valid drop target"""

class Ondragstart(HtmlAttribute):
    """Script to be run at the start of a drag operation"""

class Ondrop(HtmlAttribute):
    """Script to be run when dragged element is being dropped"""

class Ondurationchange(HtmlAttribute):
    """Script to be run when the length of the media changes"""
    parent_tags = frozenset(('Audio', 'Video'))

class Onemptied(HtmlAttribute):
    """Script to be run when something bad happens and the file is suddenly 
    unavailable (like unexpectedly disconnects)"""
    parent_tags = frozenset(('Audio', 'Video'))

class Onended(HtmlAttribute):
    """Script to be run when the media has reach the end (a useful event for 
    messages like "thanks for listening")"""
    parent_tags = frozenset(('Audio', 'Video'))

class Onerror(HtmlAttribute):
    """Script to be run when an error occurs"""
    parent_tags = frozenset(('Audio', 'Body', 'Embed', 'Img', 'Object', 'Script', 'Style', 'Video'))

class Onfocus(HtmlAttribute):
    """Script to be run when the element gets focus"""

class Onhashchange(HtmlAttribute):
    """Script to be run when there has been changes to the anchor part of the a URL"""
    parent_tags = frozenset(('Body',))

class Oninput(HtmlAttribute):
    """Script to be run when the element gets user input"""

class Oninvalid(HtmlAttribute):
    """Script to be run when the element is invalid"""

class Onkeydown(HtmlAttribute):
    """Script to be run when a user is pressing a key"""

class Onkeypress(HtmlAttribute):
    """Script to be run when a user presses a key"""

class Onkeyup(HtmlAttribute):
    """Script to be run when a user releases a key"""

class Onload(HtmlAttribute):
    """Script to be run when the element is finished loading"""
    parent_tags = frozenset(('Body', 'Iframe', 'Img', 'Input', 'Link', 'Script', 'Style'))

class Onloadeddata(HtmlAttribute):
    """Script to be run when media data is loaded"""
    parent_tags = frozenset(('Audio', 'Video'))

class Onloadedmetadata(HtmlAttribute):
    """Script to be run when meta data (like dimensions and duration) are loaded"""
    parent_tags = frozenset(('Audio', 'Video'))

class Onloadstart(HtmlAttribute):
    """Script to be run just as the file begins to load before anything is actually 
    loaded"""
    parent_tags = frozenset(('Audio', 'Video'))

class Onmousedown(HtmlAttribute):
    """Script to be run when a mouse button is pressed down on an element"""

class Onmousemove(HtmlAttribute):
    """Script to be run as long as the  mouse pointer is moving over an element"""

class Onmouseout(HtmlAttribute):
    """Script to be run when a mouse pointer moves out of an element"""

class Onmouseover(HtmlAttribute):
    """Script to be run when a mouse pointer moves over an element"""

class Onmouseup(HtmlAttribute):
    """Script to be run when a mouse button is released over an element"""

class Onmousewheel(HtmlAttribute):
    """Script to be run when a mouse wheel is being scrolled over an element"""

class Onoffline(HtmlAttribute):
    """Script to be run when the browser starts to work offline"""
    parent_tags = frozenset(('Body',))

class Ononline(HtmlAttribute):
    """Script to be run when the browser starts to work online"""
    parent_tags = frozenset(('Body',))

class Onpageshow(HtmlAttribute):
    """Script to be run when a user navigates to a page"""
    parent_tags = frozenset(('Body',))

class Onpaste(HtmlAttribute):
    """Script to be run when the user pastes some content in an element"""

class Onpause(HtmlAttribute):
    """Script to be run when the media is paused either by the user or 
    programmatically"""
    parent_tags = frozenset(('Audio', 'Video'))

class Onplay(HtmlAttribute):
    """Script to be run when the media has started playing"""
    parent_tags = frozenset(('Audio', 'Video'))

class Onplaying(HtmlAttribute):
    """Script to be run when the media has started playing"""
    parent_tags = frozenset(('Audio', 'Video'))

class Onprogress(HtmlAttribute):
    """Script to be run when the browser is in the process of getting the media 
    data"""
    parent_tags = frozenset(('Audio', 'Video'))

class Onratechange(HtmlAttribute):
    """Script to be run each time the playback rate changes (like when a user 
    switches to a slow motion or fast forward mode)."""
    parent_tags = frozenset(('Audio', 'Video'))

class Onreset(HtmlAttribute):
    """Script to be run when a reset button in a form is clicked."""
    parent_tags = frozenset(('Form',))

class Onresize(HtmlAttribute):
    """Script to be run when the browser window is being resized."""
    parent_tags = frozenset(('Body',))

class Onscroll(HtmlAttribute):
    """Script to be run when an element's scrollbar is being scrolled"""

class Onsearch(HtmlAttribute):
    """Script to be run when the user writes something in a search field (for 
    <input type="search">)"""
    parent_tags = frozenset(('Input',))

class Onseeked(HtmlAttribute):
    """Script to be run when the seeking attribute is set to false indicating that 
    seeking has ended"""
    parent_tags = frozenset(('Audio', 'Video'))

class Onseeking(HtmlAttribute):
    """Script to be run when the seeking attribute is set to true indicating that 
    seeking is active"""
    parent_tags = frozenset(('Audio', 'Video'))

class Onselect(HtmlAttribute):
    """Script to be run when the element gets selected"""

class Onstalled(HtmlAttribute):
    """Script to be run when the browser is unable to fetch the media data for 
    whatever reason"""
    parent_tags = frozenset(('Audio', 'Video'))

class Onsubmit(HtmlAttribute):
    """Script to be run when a form is submitted"""
    parent_tags = frozenset(('Form',))

class Onsuspend(HtmlAttribute):
    """Script to be run when fetching the media data is stopped before it is 
    completely loaded for whatever reason"""
    parent_tags = frozenset(('Audio', 'Video'))

class Ontimeupdate(HtmlAttribute):
    """Script to be run when the playing position has changed (like when the user 
    fast forwards to a different point in the media)"""
    parent_tags = frozenset(('Audio', 'Video'))

class Ontoggle(HtmlAttribute):
    """Script to be run when the user opens or closes the <details> element"""
    parent_tags = frozenset(('Details',))

class Onunload(HtmlAttribute):
    """Script to be run when a page has unloaded (or the browser window has been 
    closed)"""
    parent_tags = frozenset(('Body',))

class Onvolumechange(HtmlAttribute):
    """Script to be run each time the volume of a video/audio has been changed"""
    parent_tags = frozenset(('Audio', 'Video'))

class Onwaiting(HtmlAttribute):
    """Script to be run when the media has paused but is expected to resume (like 
    when the media pauses to buffer more data)"""
    parent_tags = frozenset(('Audio', 'Video'))

class Onwheel(HtmlAttribute):
    """Script to be run when the mouse wheel rolls up or down over an element"""

class Open(BooleanHtmlAttribute):
    """Specifies that the details should be visible (open) to the user"""
    parent_tags = frozenset(('Details',))

class Optimum(HtmlAttribute):
    """Specifies what value is the optimal value for the gauge"""
    parent_tags = frozenset(('Meter',))

class Pattern(HtmlAttribute):
    """Specifies a regular expression that an <input> element's value is checked 
    against"""
    parent_tags = frozenset(('Input',))

class Placeholder(HtmlAttribute):
    """Specifies a short hint that describes the expected value of the element"""
    parent_tags = frozenset(('Input', 'Textarea'))

class Popover(HtmlAttribute):
    """Specifies a popover element"""

class Popovertarget(HtmlAttribute):
    """Specifies which popover element to invoked"""
    parent_tags = frozenset(('Button', 'Input'))

class Popovertargetaction(HtmlAttribute):
    """Specifies what happens to the popover element when the button is clicked"""
    parent_tags = frozenset(('Button', 'Input'))

class Poster(HtmlAttribute):
    """Specifies an image to be shown while the video is downloading, or until the 
    user hits the play button"""
    parent_tags = frozenset(('Video',))

class Preload(HtmlAttribute):
    """Specifies if and how the author thinks the audio/video should be loaded when 
    the page loads"""
    parent_tags = frozenset(('Audio', 'Video'))

class Readonly(BooleanHtmlAttribute):
    """Specifies that the element is read-only"""
    parent_tags = frozenset(('Input', 'Textarea'))

class Rel(HtmlAttribute):
    """Specifies the relationship between the current document and the linked 
    document"""
    parent_tags = frozenset(('A', 'Area', 'Form', 'Link'))

class Required(BooleanHtmlAttribute):
    """Specifies that the element must be filled out before submitting the form"""
    parent_tags = frozenset(('Input', 'Select', 'Textarea'))

class Reversed(BooleanHtmlAttribute):
    """Specifies that the list order should be descending (9,8,7...)"""
    parent_tags = frozenset(('Ol',))

class Rows(HtmlAttribute):
    """Specifies the visible number of lines in a text area"""
    parent_tags = frozenset(('Textarea',))

class Rowspan(HtmlAttribute):
    """Specifies the number of rows a table cell should span"""
    parent_tags = frozenset(('Td', 'Th'))

class Sandbox(HtmlAttribute):
    """Enables an extra set of restrictions for the content in an <iframe>"""
    parent_tags = frozenset(('Iframe',))

class Scope(HtmlAttribute):
    """Specifies whether a header cell is a header for a column, row, or group of 
    columns or rows"""
    parent_tags = frozenset(('Th',))

class Selected(BooleanHtmlAttribute):
    """Specifies that an option should be pre-selected when the page loads"""
    parent_tags = frozenset(('Option',))

class Shape(HtmlAttribute):
    """Specifies the shape of the area"""
    parent_tags = frozenset(('Area',))

class Size(HtmlAttribute):
    """Specifies the width, in characters (for <input>) or specifies the number of 
    visible options (for <select>)"""
    parent_tags = frozenset(('Input', 'Select'))

class Sizes(HtmlAttribute):
    """Specifies the size of the linked resource"""
    parent_tags = frozenset(('Img', 'Link', 'Source'))

class Span_(HtmlAttribute):
    """Specifies the number of columns to span"""
    display_name: str = 'span'
    parent_tags = frozenset(('Col', 'Colgroup'))

class Spellcheck(HtmlAttribute):
    """Specifies whether the element is to have its spelling and grammar checked or 
    not"""

class Src(HtmlAttribute):
    """Specifies the URL of the media file"""
    parent_tags = frozenset(('Audio', 'Embed', 'Iframe', 'Img', 'Input', 'Script', 'Source', 'Track', 'Video'))

class Srcdoc(HtmlAttribute):
    """Specifies the HTML content of the page to show in the <iframe>"""
    parent_tags = frozenset(('Iframe',))

class Srclang(HtmlAttribute):
    """Specifies the language of the track text data (required if kind="subtitles")"""
    parent_tags = frozenset(('Track',))

class Srcset(HtmlAttribute):
    """Specifies the URL of the image to use in different situations"""
    parent_tags = frozenset(('Img', 'Source'))

class Start(HtmlAttribute):
    """Specifies the start value of an ordered list"""
    parent_tags = frozenset(('Ol',))

class Step(HtmlAttribute):
    """Specifies the legal number intervals for an input field"""
    parent_tags = frozenset(('Input',))

class Tabindex(HtmlAttribute):
    """Specifies the tabbing order of an element"""

class Target(HtmlAttribute):
    """Specifies the target for where to open the linked document or where to 
    submit the form"""
    parent_tags = frozenset(('A', 'Area', 'Base', 'Form'))

class Title_(HtmlAttribute):
    """Specifies extra information about an element"""
    display_name: str = 'title'

class Translate(HtmlAttribute):
    """Specifies whether the content of an element should be translated or not"""

class Type(HtmlAttribute):
    """Specifies the type of element"""
    parent_tags = frozenset(('A', 'Button', 'Embed', 'Input', 'Link', 'Menu', 'Object', 'Script', 'Source', 'Style'))

class Usemap(HtmlAttribute):
    """Specifies an image as a client-side image map"""
    parent_tags = frozenset(('Img', 'Object'))

class Value(HtmlAttribute):
    """Specifies the value of the element"""
    parent_tags = frozenset(('Button', 'Input', 'Li', 'Option', 'Meter', 'Progress', 'Param'))

class Width(HtmlAttribute):
    """Specifies the width of the element"""
    parent_tags = frozenset(('Embed', 'Iframe', 'Img', 'Input', 'Object', 'Video'))

class Wrap(HtmlAttribute):
    """Specifies how the text in a text area is to be wrapped when submitted in a 
    form"""
    parent_tags = frozenset(('Textarea',))