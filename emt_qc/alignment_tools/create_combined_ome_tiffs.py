import os
from pathlib import Path

import numpy as np
from aicsimageio import AICSImage
from aicsimageio.writers import OmeTiffWriter

from emt_qc.alignment_tools.align_emt import align_emt

dir = '/allen/aics/microscopy/Aditya/EMT_test_data/5500000640_EE_2-01/aligned_split'

# Create a dictionary that contains empty arrays that can be filled with image data
# Created one per scene imaged in the EMT timelapse, so each scene can be combined separately
# aicsimageio writes lists of files, each being a separate scene, but we are creating individual
# files for each scene so that they can be loaded into fiji quickly
# Each array is a 5D array, order TCZYX. T corresponds to block #.
# T:7, C:4, Z:40, Y:1200, X:1800'


def gen_single_scene_timelapse_comb_file(emt_exp_dir: str) -> Path:
	
	aligned_dir = Path(f'{emt_exp_dir}/aligned_split')
	
	if not os.path.exists(aligned_dir / "combined_images"):
		os.mkdir(aligned_dir / "combined_images")
	for scene in range(28):
		comb_array =  np.zeros([7,4,40,1200,1800], dtype = 'uint16')
		for _, _, filenames in os.walk(aligned_dir):
			for filename in [f for f in filenames if f.endswith('.tiff')]:
				if 'argo' not in filename and 'aligned_timelapse.ome.tiff' not in filename:
					block_num = int(filename[filename.find('Block') + 5 : filename.find('Block') + 6])
					scene_num = int(filename[filename.find('Scene') + 6 : filename.find('_aligned')])
					if scene_num == scene:
						if block_num == 7:
							comb_array[block_num-1] = AICSImage(os.path.join(aligned_dir, filename)).data.astype('uint16')
							print(f'{filename} added: Scene:{scene_num} Block:{block_num}')
						elif 0 < block_num < 7:
							comb_array[block_num-1,0:2] = AICSImage(os.path.join(aligned_dir, filename)).data.astype('uint16')
							print(f'{filename} added: Scene:{scene_num} Block:{block_num}')
		
		OmeTiffWriter.save(comb_array, aligned_dir / f'combined_images' / f'{os.path.split(aligned_dir.parent)[-1]}_Scene-{scene}_aligned_timelapse.ome.tiff')
		print(f'Created aligned timelapse image for P{scene}')

	return aligned_dir / 'combined_images'
	




#	OmeTiffWriter.save(list(comb_dict.values()),'/allen/aics/microscopy/Aditya/EMT_test_data/5500000640_EE_2-01/test_images/5500000640_EE_2-01_16bit_aligned_timelapse.ome.tiff')
	# possibly annotate metadata on upload, and allow the metadata service to populate the ome_metadata
