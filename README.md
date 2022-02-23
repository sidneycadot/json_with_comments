# json_with_comments
A sane way to add comments to JSON

I like JSON as a minimalistic way of representing information in a human-readable way.

It is almost suitable for configuration files, apart from the fact that it doesn't allow comments,
which is a necessity for that purpose.

One workaround is to add fields that contain comments to JSON onjects. I do not like this solution
as it clutters the object, and cannot be used in places that are not objects (like at the start of
the file, or inside arrays).

Another approach taken by some libraries is to add comments as an extension. Often times, such
libraries will also implement support for other things their authors do not like about JSON,
such as the inability to express IEEE-754 floating point values like "Inf" and "NaN", and the
ability to specify multi-line strings.

This approach has the drawback of introducing a dependency on an external package. Personally,
I try to minimize dependencies in my projects, and introducing a dependency on an package outside
the standard library that replicates functionality inside the standard library with a few additions
seems wasteful.

I therefore propose a third approach here, for working with comments in JSON.

{
}
,
:
[
]
::whitespace
::string
::number
true
false
null

::string:
  - any codepoint except " or \ or control characters;
  - \"
  - \\
  - \/
  - \b
  - \f
  - \n
  - \r
  - \t
  - \uHHHH

::number:

- optional preceding '-'
- mandatory unsigned integer (0, 1, 2, ...)
- optional fraction: dot followed by digits --- "."[0-9]+

- optional exponent: [eE][+-]?[0-9]+

::whitespace:
  - space, linefeed, carriage return, horizontal tab
