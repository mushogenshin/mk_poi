import sys
import platform
import os
import yaml
import re
import time
import subprocess
import logging
from pathlib import Path, PureWindowsPath
from distutils import dir_util

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

_CUR_DIR = Path(sys.argv[0]).parent  # use this instead of __file__ as on Windows we also build with pyinstaller


class MkPackage(object):

	_OS = platform.system()  # Windows; Darwin; Linux;

	def __init__(self, config_file):
		"""
		Parse the config file and populate object's METADATA
		:parm Path config_file: path to the .yaml file
		"""
		with open(config_file.as_posix(), 'r') as stream:

			self._METADATA = {}

			try:
				self._METADATA = yaml.safe_load(stream) # a dict
				# Add more info to the metadata
				pkg_name = config_file.stem
				self._METADATA['name'] = pkg_name
				# validity is if a folder with a same name exists
				self._METADATA['src_root'] = config_file.with_name(config_file.stem)
				self._METADATA['is_valid'] = self._METADATA['src_root'].exists()
			except yaml.YAMLError as e:
				logger.error('Unable to parse config file for package "{}" due to: {}.'.format(pkg_name, e))
			else:
				logger.debug('MkPackage "{}" initialized successfully. Is valid: {}'.format(
					pkg_name, self._METADATA['is_valid']
				))

	def install(self, do_copy=True, show_results=False):
		"""
		Perform based on an iterable dst_paths
		"""
		# Expand the destination depending on whether mutiple-versions or not
		dst_paths = self.expand_destination(multiple_versions=self._METADATA['multi_versions'])

		if do_copy:
			# Do the copy
			for dst_path in dst_paths:
				try:
					logger.debug('----Destination: {}'.format(dst_path[-1]))
					dir_util.copy_tree(self._METADATA['src_root'].as_posix(), dst_path[-1].as_posix())
				except Exception as e:
					logger.warning('------Failed to install for version "{}" due to: {}.'.format(dst_path[0], e))
				else:
					logger.debug('------Installation completed for version "{}".'.format(dst_path[0]))
		
		if show_results:
			if MkPackage._OS == "Windows":
				# Open Windows explorer
				for dst_path in dst_paths:
					subprocess.Popen(['explorer', str(PureWindowsPath(dst_path[-1]))])
			# TODO: Open Finder on MacOS

	def expand_destination(self, multiple_versions):
		"""
		:return: collection of destination paths
		:rtype: tuple of tuple, e.g. (('ZBrush 2018', Path('/path/to/dst')),)
		"""
		dst_paths = []  # result container

		os_pkg_metadata = self._METADATA.get(MkPackage._OS, {})
		if not os_pkg_metadata:
			return dst_paths

		dst_root = os_pkg_metadata.get('dst_root', "")
		dst_variant_pattern = os_pkg_metadata.get('dst_variant_pattern', "")
		dst_variant_pattern_2 = os_pkg_metadata.get('dst_variant_pattern_2', "")
		dst_subdir = os_pkg_metadata.get('dst_subdir', "")
		dst_root = Path(os.path.expandvars(dst_root))  # expand the env vars if necessary

		print("DESTINATION ROOT:", dst_root)
		if not dst_root.exists():
			logger.warning('--Non-existent destination root. Skipped.')
		else:
			if not multiple_versions:
				# Single version, just concat the path, e.g.:
				# C:\Program Files\Pixologic / ZBrush 2020 / ZStartup\BrushPresets
				root_sub_dir = dst_root / dst_variant_pattern / dst_subdir

				# Create the root dir if it doesn't exist yet
				if not (root_sub_dir.exists() or root_sub_dir.is_dir()):
					try:
						root_sub_dir.mkdir(parents=True)
					except Exception as e:
						logger.error('Unable to create sub-directory due to: {}'.format(e))
					
				version_name = dst_root.name
				# supports for proper name logging
				if dst_variant_pattern:
					version_name = dst_variant_pattern

				dst_paths.append((version_name, root_sub_dir))
				logger.debug('--Expanded destination for: single version')
			else:
				# Investigate subdirs by searching the provided regex pattern
				for root_sub_dir in dst_root.glob('*'):
					re_match = re.match(dst_variant_pattern, root_sub_dir.name)

					if re_match and root_sub_dir.is_dir():  # e.g. root_sub_dir = 'C:\Users\hoan.nguyen\Documents\maya.SPD'

						if not dst_variant_pattern_2:
							# One level only, just concat the subdir
							root_sub_dir = root_sub_dir / dst_subdir
							
							# Create the root dir if it doesn't exist yet
							if not root_sub_dir.exists():
								root_sub_dir.mkdir(parents=True)

							dst_paths.append((re_match.string, root_sub_dir))
						else:
							# Need to go one more level deep, e.g. Maya
							for root_sub_dir_nested in root_sub_dir.glob('*'):
								re_match_2 = re.match(dst_variant_pattern_2, root_sub_dir_nested.name)

								if re_match_2 and root_sub_dir_nested.is_dir():  # e.g. root_sub_dir_nested = 'C:\Users\hoan.nguyen\Documents\maya.SPD\2018'
									# Now concat the subdir
									root_sub_dir_nested = root_sub_dir_nested / dst_subdir
									
									# Create the root dir if it doesn't exist yet
									if not root_sub_dir.exists():
										root_sub_dir.mkdir(parents=True)

									dst_paths.append((re_match_2.string, root_sub_dir_nested))
				logger.debug('--Expanded destinations for: multiple versions')

		# logger.debug('--All destinations: \n')
		# for dst_path in dst_paths:
		# 	logger.debug('----{}'.format(str(dst_path)))

		return tuple(dst_paths)


def install_all(target_dir=None, do_copy=True, show_results=False):
	"""
	:parm Path target_dir: whether to look for a specific target folder, 
						if False: automatically search recursively within _CUR_DIR
	"""
	# Look for valid packages to install
	_CFG_FILE_EXT = '.yaml'
	global _CUR_DIR

	_CUR_DIR = target_dir if target_dir else _CUR_DIR

	pkg_cfgs = tuple(_CUR_DIR.rglob('*' + _CFG_FILE_EXT))
	logger.debug('\n***Found {} config file(s).\n'.format(len(pkg_cfgs)))

	for pkg_cfg in pkg_cfgs:

		mk_package = MkPackage(pkg_cfg)  # new MkPackage object from the config file

		if mk_package._METADATA['is_valid']:  # must at least has the folder data

			logger.debug('--Reading package "{}" on {}...'.format(
				mk_package._METADATA['name'], MkPackage._OS
			))

			# Abbreviated logging
			src_root = mk_package._METADATA['src_root']  # short hand
			src_path_trimmed = (src_root / "../../..").resolve()
			logger.debug('--Source root: ./{}'.format(src_root.relative_to(src_path_trimmed)))

			mk_package.install(do_copy, show_results)
			

if __name__ == '__main__':

	if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
		# Called from compiled .exe on Windows
		# SLEEP = 30
		# install_all()
		# time.sleep(SLEEP)
		pass
	else:
		# Running from Python file
		# SANDBOX_DIR = 'packages_private/ZBrush'
		# install_all(target_dir=(_CUR_DIR / SANDBOX_DIR), do_copy=True, show_results=False)
		install_all(do_copy=True, show_results=False)
		pass

	pass
