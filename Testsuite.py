# EMACS settings: -*-	tab-width: 2; indent-tabs-mode: t; python-indent-offset: 2 -*-
# vim: tabstop=2:shiftwidth=2:noexpandtab
# kate: tab-width 2; replace-tabs off; indent-width 2;
# ==============================================================================
# Authors:            Patrick Lehmann
#
# Python functions:   A streaming VHDL parser
#
# Description:
# ------------------------------------
#		TODO:
#
# License:
# ==============================================================================
# Copyright 2007-2016 Patrick Lehmann - Dresden, Germany
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
#
from pathlib import Path

import sys

from src.Base               import ParserException
from src.Filters.Comment     import StripAndFuse
from src.Functions          import Console, Exit
from src.Token.Tokens       import EndOfDocumentToken
from src.Token.Parser       import Tokenizer, StartOfDocumentToken
from src.Blocks.Document    import StartOfDocumentBlock, EndOfDocumentBlock
from src.Blocks.Parser      import TokenToBlockParser

from test                   import LibraryTest, UseTest, EntityTest, GenericListTest, PortListTest, ArchitectureTest, ProcessTest


Console.init()

rootDirectory = Path(".")
vhdlDirectory = rootDirectory / "vhdl"

testCases = [
	LibraryTest.TestCase,
	UseTest.TestCase,
	EntityTest.TestCase,
	GenericListTest.TestCase,
	PortListTest.TestCase,
	ArchitectureTest.TestCase,
	ProcessTest.TestCase
]

alphaCharacters = Tokenizer.__ALPHA_CHARS__ + "_" + Tokenizer.__NUMBER_CHARS__

runExpectedBlocks =           True
runExpectedBlocksAfterStrip = not True
runConnectivity =             True

for testCase in testCases:
	print("Testcase: {CYAN}{name}.{NOCOLOR}".format(name=testCase.__NAME__, **Console.Foreground))

	file = vhdlDirectory / testCase.__FILENAME__

	if (not file.exists()):
		print("  {RED}File '{0!s}' does not exist.{NOCOLOR}".format(file, **Console.Foreground))
		continue

	with file.open('r') as fileHandle:
		content = fileHandle.read()

	# History check
	if runExpectedBlocks:
		counter =         testCase.GetExpectedBlocks()
		wordTokenStream = Tokenizer.GetWordTokenizer(content, alphaCharacters=alphaCharacters, numberCharacters="")
		vhdlBlockStream = TokenToBlockParser.Transform(wordTokenStream)

		try:
			for vhdlBlock in vhdlBlockStream:
				counter.Count(vhdlBlock.__class__)

			if counter.Check():
				print("  History check - PASSED")
			else:
				counter.PrintReport()
				print("  History check - FAILED")

		except ParserException as ex:     print("ERROR: " + str(ex))
		except NotImplementedError as ex: print("NotImplementedError: " + str(ex))

	# History check
	if runExpectedBlocksAfterStrip:
		counter =             testCase.GetExpectedBlocksAfterStrip()
		wordTokenStream =     Tokenizer.GetWordTokenizer(content, alphaCharacters=alphaCharacters, numberCharacters="")
		vhdlBlockStream =     TokenToBlockParser.Transform(wordTokenStream)
		strippedBlockStream = StripAndFuse(vhdlBlockStream)

		try:
			for vhdlBlock in strippedBlockStream:
				counter.Count(vhdlBlock.__class__)

			if counter.Check():
				print("  History check - PASSED")
			else:
				counter.PrintReport()
				print("  History check - FAILED")

		except ParserException as ex:     print("ERROR: " + str(ex))
		except NotImplementedError as ex: print("NotImplementedError: " + str(ex))


	# Connectivity check
	if runConnectivity:
		wordTokenStream = Tokenizer.GetWordTokenizer(content, alphaCharacters=alphaCharacters, numberCharacters="")
		vhdlBlockStream = TokenToBlockParser.Transform(wordTokenStream)

		try:
			blockIterator = iter(vhdlBlockStream)
			firstBlock =    next(blockIterator)
			if (not isinstance(firstBlock, StartOfDocumentBlock)):              print("{RED}First block is not StartOfDocumentBlock: {block}{NOCOLOR}".format(block=firstBlock, **Console.Foreground))
			elif (not isinstance(firstBlock.StartToken, StartOfDocumentToken)): print("{RED}First token is not StartOfDocumentToken: {token}{NOCOLOR}".format(token=firstBlock.StartToken, **Console.Foreground))

			lastBlock = None
			lastToken = firstBlock.StartToken
			for vhdlBlock in blockIterator:
				if isinstance(vhdlBlock, EndOfDocumentBlock):
					lastBlock = vhdlBlock
					break
				tokenIterator = iter(vhdlBlock)

				for token in tokenIterator:
					if (token.NextToken is None):                 print("{RED}Token has an open end.{NOCOLOR}".format(**Console.Foreground))
					elif (lastToken.NextToken is not token):      print("{RED}Last token is not connected to the current one.{NOCOLOR}".format(**Console.Foreground))
					elif (token.PreviousToken is not lastToken):  print("{RED}Current token is not connected to lastToken.{NOCOLOR}".format(**Console.Foreground))
					lastToken = token
			else:
				print("{RED}No EndOfDocumentBlock found.{NOCOLOR}".format(**Console.Foreground))

			if (not isinstance(lastBlock, EndOfDocumentBlock)):              print("{RED}Last block is not EndOfDocumentBlock: {block}{NOCOLOR}".format(block=lastBlock, **Console.Foreground))
			elif (not isinstance(lastBlock.StartToken, EndOfDocumentToken)): print("{RED}Last block is not EndOfDocumentToken: {token}{NOCOLOR}".format(token=lastBlock.StartToken, **Console.Foreground))

		except ParserException as ex:     print("ERROR: " + str(ex))
		except NotImplementedError as ex: print("NotImplementedError: " + str(ex))

	print()

print("COMPLETED")
