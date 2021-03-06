# Copyright (C) 2014 Google Inc.
#
# This file is part of ycmd.
#
# ycmd is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# ycmd is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with ycmd.  If not, see <http://www.gnu.org/licenses/>.

import difflib
import inspect
import os
import sys
import ycm_core

flags = [
'-x',
'c++',
'-Wall',
'-Wextra',
'-Werror',
'-fexceptions',
'-DNDEBUG',
'-std=c++14'
]

def DirectoryOfThisScript():
  return os.path.dirname( os.path.abspath( __file__ ) )

SOURCE_EXTENSIONS = [ '.cpp', '.cxx', '.cc', '.c', '.m', '.mm' ]
rootdir = DirectoryOfThisScript()
compilation_database_folder = rootdir

if os.path.exists( compilation_database_folder ):
  database = ycm_core.CompilationDatabase( compilation_database_folder )
else:
  database = None

def MakeRelativePathsInFlagsAbsolute( flags, working_directory ):
  if not working_directory:
    return list( flags )
  new_flags = []
  make_next_absolute = False
  path_flags = [ '-isystem', '-I', '-iquote', '--sysroot=' ]
  for flag in flags:
    new_flag = flag

    if make_next_absolute:
      make_next_absolute = False
      if not flag.startswith( '/' ):
        new_flag = os.path.join( working_directory, flag )

    for path_flag in path_flags:
      if flag == path_flag:
        make_next_absolute = True
        break

      if flag.startswith( path_flag ):
        path = flag[ len( path_flag ): ]
        new_flag = path_flag + os.path.join( working_directory, path )
        break

    if new_flag:
      new_flags.append( new_flag )
  return new_flags


def IsHeaderFile( filename ):
  extension = os.path.splitext( filename )[ 1 ]
  return extension in [ '.h', '.hxx', '.hpp', '.hh' ]

def GetSourceFileScore( header, source ):
  diff = difflib.ndiff(header.split('/'), source.split('/'))
  return sum(1 if line[:2] == '  ' else 0 for line in diff)

def GetSourceFileForHeader( filename ):
  basename = os.path.basename( filename )
  unextended_basename = os.path.splitext( basename )[ 0 ]
  max_score = 0
  result = None
  for (dirname, dirs, files) in os.walk(rootdir):
    for extension in SOURCE_EXTENSIONS:
      replacement_file = unextended_basename + extension
      if replacement_file in files:
        candidate = os.path.join(dirname, replacement_file)
        score = GetSourceFileScore(filename, candidate)
        if score > max_score:
          max_score = score
          result = candidate
  if result:
    return result
  else:
    raise Exception( 'Cannot find source file for {}'.format( filename ) )

def GetCompilationInfoForFile( filename ):
  # The compilation_commands.json file generated by CMake does not have entries
  # for header files. So we do our best by asking the db for flags for a
  # corresponding source file, if any. If one exists, the flags for that file
  # should be good enough.
  if IsHeaderFile( filename ):
    try:
      compilation_info = database.GetCompilationInfoForFile(
        GetSourceFileForHeader( filename ) )
      if compilation_info.compiler_flags_:
        return compilation_info
    except:
      pass
  return database.GetCompilationInfoForFile( filename )


# This is the entry point; this function is called by ycmd to produce flags for
# a file.
def FlagsForFile( filename, **kwargs ):
  final_flags = None
  if database:
    # Bear in mind that compilation_info.compiler_flags_ does NOT return a
    # python list, but a "list-like" StringVec object
    compilation_info = GetCompilationInfoForFile( filename )
    if compilation_info:
      final_flags = MakeRelativePathsInFlagsAbsolute(
        compilation_info.compiler_flags_,
        compilation_info.compiler_working_dir_ )
  if not final_flags:
    relative_to = DirectoryOfThisScript()
    final_flags = MakeRelativePathsInFlagsAbsolute( flags, relative_to )

  return { 'flags': final_flags }
