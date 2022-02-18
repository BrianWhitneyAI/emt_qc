from aicsimageio import AICSImage
from aicsimageio.writers import OmeTiffWriter
import numpy as np
import os
from pathlib import Path

dir = '/allen/aics/microscopy/Aditya/EMT_test_data/5500000640_EE_2-01/aligned_split'

# Create a dictionary that contains empty arrays that can be filled with image data
# Created one per scene imaged in the EMT timelapse, so each scene can be combined separately 
# aicsimageio writes lists of files, each being a separate scene, but we are creating individual 
# files for each scene so that they can be loaded into fiji quickly
# Each array is a 5D array, order TCZYX. T corresponds to block #.
# T:7, C:4, Z:40, Y:1200, X:1800

def gen_single_scene_timelapse_comb_file(emt_exp_dir: str):
#	comb_dict = {}
#	for scene in range(28):
#		comb_dict[scene] = np.zeros([7,4,40,1200,1800], dtype = 'uint16')
	aligned_dir = Path(f'{emt_exp_dir}/aligned_split')
	if not os.path.exists(aligned_dir / "combined_images"):
		os.mkdir(aligned_dir / "combined_images")

	# Iterate through all aligned_split files and place them into the corresponding array in the dictionary initialized above
	for scene in range(28):
		for dirpath, dirnames, filenames in os.walk(aligned_dir):
			comb_array = np.zeros([7,4,40,1200,1800], dtype = 'uint16')
			for filename in [f for f in filenames if f.endswith('.tiff')]:
				if 'argo' not in filename:
					block_num = int(filename[filename.find('Block') + 5 : filename.find('Block') + 6])
					scene_num = int(filename[filename.find('Scene') + 6 : filename.find('_aligned')])
					if block_num == 7:
						comb_array[block_num-1] = AICSImage(os.path.join(aligned_dir, filename)).data.astype('uint16')
						print(f'{filename} added: Scene:{scene_num} Block:{block_num}')
					elif 0 < block_num < 7:
						comb_array[block_num-1,0:2] = AICSImage(os.path.join(aligned_dir, filename)).data.astype('uint16')
						print(f'{filename} added: Scene:{scene_num} Block:{block_num}')
			OmeTiffWriter.save(comb_array, aligned_dir / f'combined_images/')


#	OmeTiffWriter.save(list(comb_dict.values()),'/allen/aics/microscopy/Aditya/EMT_test_data/5500000640_EE_2-01/test_images/5500000640_EE_2-01_16bit_aligned_timelapse.ome.tiff')
	# possibly annotate metadata on upload, and allow the metadata service to populate the ome_metadata