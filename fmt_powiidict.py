from inc_noesis import *
import rapi
import os

# registerNoesisTypes is called by Noesis to allow the script to register formats.
# Do not implement this function in script files unless you want them to be dedicated format modules!
def registerNoesisTypes():
    """
    Registers the .dict file type as a possible choice to select. Runs code to check its validity and extract
    information.
    :return: 1
    """
    handle = noesis.register("Punch-Out!! Wii Data/Dict pair", ".dict")
    noesis.setHandlerTypeCheck(handle, CheckDictType)
    noesis.setHandlerLoadModel(handle, ExtractDict)
    noesis.logPopup()
    print(
        "The log can be useful for catching debug prints from preview loads.\nBut don't leave it on when you release your script, or it will probably annoy people.")
    return 1


def CheckDictType(data):
    """
    Confirms whether the header or the length is of the proper size.
    :param data: File data coming in
    :return: 0 for fail 1 for pass
    """
    # Starts reading data
    bs = NoeBitStream(data)
    if len(data) < 58:
        print("Invalid dict file, too small")
        return 0
    if bs.readInt() != 0x5824F3A9:
        print("Your header is incorrect, or the byte order is wrong.")
        return 0
    return 1


def ExtractDict(data, mdlList):
    """
	Collects the block information from the .dict file and will recieve all the parsed information from
	another function later in the code.
	:param data: File data coming in
	:param mdlList: no idea
	:return: not sure yet either
	"""

    # Starts the rapi module to create things to put in
    ctx = rapi.rpgCreateContext()

    # Start reading data
    bs = NoeBitStream(data)

    # Sets to big endian because PO is often big endian
    bs.setEndian(bigEndian=True)

    # Sets offset to where the file entries and sizes are read
    bs.setOffset(0x10)

    # Reads file entries and sizes
    file_entries = bs.readUInt()
    file_sizes = bs.readUInt()

    block_count = 0
    block_offset = 0

    # Will store the information about the blocks as a tuple, (block_offset, block_size, block_type)
    block_list = []
    while block_count < 8:
        # Gets size of block
        block_size = bs.readUInt()

        # Gets the type of a block, which is either 0x04 or 0x32
        block_type = bs.readUInt()

        # Saves information in a tuple to keep it safe
        block_information = (block_offset, block_size, block_type)

        # Places tuple in list for further reading if block is used
        if (block_information[2] != 0):
            block_list.append(block_information)
        else:
            pass

        # Sets offset each time
        block_offset = block_offset + block_size

        block_count += 1
    global dataFileName
    global fileName
    dataFileName = rapi.getInputName()[:-5] + ".data"
    fileName = os.path.dirname(rapi.getInputName()) + os.sep + rapi.getLocalFileName(dataFileName)[:-5]

    #Creates second bytestream
    bds = NoeBitStream(rapi.loadIntoByteArray(dataFileName), 1)
    bds.setEndian(bigEndian=True)


    all_chunk_info = splitDataFileChunks(block_list, file_entries)
    parsed_data = parseDataFileChunks(all_chunk_info, block_list)


    mdl = rapi.rpgConstructModel()
    mdl.setBones(parsed_data)
    mdlList.append(mdl)

    return 1


def splitDataFileChunks(block_list, file_entries):
    """
	Takes the block information and begins to inspect chunks inside the file.
	Then from these chunks, obtain the information needed for a .dae export
	:param block_list: Tuple containing (offset, size, type) for a block of data
	:return: Tuple containing (type, size, offset, index, and flag)
	"""

    # Gets offset of chunk list from block_list
    final_block = block_list[-1]
    chunk_table_offset = final_block[0] + final_block[1]

    bds = NoeBitStream(rapi.loadIntoByteArray(dataFileName), 1)
    bds.setEndian(bigEndian=True)
    bds.setOffset(chunk_table_offset)
    counter = 0
    # saves chunk information if needed later
    chunk_info = []
    # reads chunk information but I'm not sure if we'll need it for now
    while counter < file_entries:
        # Chunk flag
        chunkFlags = bds.readBytes(1)

        # Always equals 1, unknown
        always1 = bds.readByte()

        # Chunk type
        chunk_type = bds.readBytes(2)

        # Size of the chunk
        chunk_size = bds.readUInt()

        # Chunk offset
        chunk_offset = bds.readUInt()

        # saves information
        chunk_tuples = (chunkFlags, chunk_type, chunk_size, chunk_offset)
        chunk_info.append(chunk_tuples)

        counter += 1

    current_location = bds.getOffset()

    # Dictionary of all known chunk types
    known_chunks = {
        0xB601: "TextureHeaders",
        0xB603: "TextureData",
        0xB016: "MaterialData",
        0xB007: "IndexData",
        0xB006: "VertexData",
        0xB005: "VertexAttributePointerData",
        0xB004: "MeshData",
        0xB003: "ModelData",
        0xB002: "MatrixData",
        0xB008: "SkeletonData",
        0xB00B: "BoneHashes",
        0xB00A: "BoneData",
        0xB00C: "UnknownHashList",
        0x7002: "AnimationName",
        0x7101: "AnimBoneRotation",
        0x7102: "AnimBoneTransformation",
        0x7103: "AnimBoneScale",
        0x8002: "Model Name",
        0x8003: "Joint Hash List",
        0x8009: "Joint Parenting List",
        0x8010: "Joint Poistion Vectors"}

    all_chunk_data_list = []

    while current_location < len(bds.data) - 12:
        # Chunk start flag and sets index
        chunk_flag_2 = bds.readByte()
        # sets chunk index, i tried but honestly it's just not working so go bother switch toolbox for better understanding
        if (chunk_flag_2 == 18):
            chunk_index = 0
        elif (chunk_flag_2 == 37):
            chunk_index = 1
        elif (chunk_flag_2 == 2):
            chunk_index = 2
        elif (chunk_flag_2 == 66):
            chunk_index = 3
        elif (chunk_flag_2 == 3):
            chunk_index = 0
        else:
            block_flag = chunk_flag_2 >> 4
            if (block_flag < 7):
                chunk_index = block_flag
            else:
                chunk_index = None

        # Always equals 1, unknown
        always1_2 = bds.readByte()

        # Gets the type of chunk, corresponds to certain name/action
        chunk_type_2 = bds.readUShort()

        # Gets size of said chunk
        chunk_size_2 = bds.readUInt()

        # The offset of the chunk
        chunk_offset_2 = bds.readUInt()

        # stores all chunks in a list for further processing outside of loop

        chunk_information_tuple = (chunk_type_2, chunk_size_2, chunk_offset_2, chunk_index, chunk_flag_2)
        all_chunk_data_list.append(chunk_information_tuple)

        # Updates current offset to avoid re-reading the file
        current_location = bds.getOffset()
    return (all_chunk_data_list)


def parseDataFileChunks(all_chunk_data_list, block_list):
    bds = NoeBitStream(rapi.loadIntoByteArray(dataFileName), 1)
    bds.setEndian(bigEndian=True)

    known_chunks = {
        0xB601: "TextureHeaders",
        0xB603: "TextureData",
        0xB016: "MaterialData",
        0xB007: "IndexData",
        0xB006: "VertexData",
        0xB005: "VertexAttributePointerData",
        0xB004: "MeshData",
        0xB003: "ModelData",
        0xB002: "MatrixData",
        0xB008: "SkeletonData",
        0xB00B: "BoneHashes",
        0xB00A: "BoneData",
        0xB00C: "UnknownHashList",
        0x7002: "AnimationName",
        0x7101: "AnimBoneRotation",
        0x7102: "AnimBoneTransformation",
        0x7103: "AnimBoneScale",
        0x8002: "Model Name",
        0x8003: "Bone Hash List(?)",
        0x8009: "Bone Parenting List (?)"}

    bone_maps = []
    vertex_items_length = []
    vertex_attribute_data_list = []
    joint_parent_order = []
    bone_position = []
    some_bone_matrices = []

    model_counter = -1


    joint_list = []
    hash_to_mat = {}
    pList = []
    hashList = []


    for saved in all_chunk_data_list:
        if saved[0] == 0xB004:
            block_index = block_list[1]
            block_offset = block_index[0]
            total_offset = block_offset + saved[2] + 6
            size_limit = block_offset + saved[2] + saved[1]
            model_counter += 1
            while total_offset <= size_limit:
                bds.setOffset(total_offset)
                faces_count = bds.readUShort()
                item_length = bds.readUShort()
                mesh_tuples = (item_length, faces_count, model_counter)
                # Add amount of vertices to list for future use
                vertex_items_length.append(mesh_tuples)
                total_offset += 52

    for saved in all_chunk_data_list:
        if saved[0] == 0xB005:
            block_index = block_list[1]
            block_offset = block_index[0]
            total_offset = block_offset + saved[2]
            size_limit = block_offset + saved[2] + saved[1]
            while total_offset < size_limit:
                bds.setOffset(total_offset)
                vertices_offset = bds.readUInt()
                section_type = bds.readUByte()
                section_stride = bds.readUByte()
                not_necessary = bds.readShort()
                saving_tuple = (vertices_offset, section_type, section_stride)
                vertex_attribute_data_list.append(saving_tuple)
                total_offset = bds.getOffset()

    for saved in all_chunk_data_list:
        # For bones
        if saved[0] == 0xB00A:
            # Get offset where bone 4x3 matrices are
            block_index = block_list[1]
            block_offset = block_index[0]
            total_offset = block_offset + saved[2]
            size_limit = block_offset + saved[2] + saved[1]

            # While within size limit, read location of bones
            while total_offset < size_limit:
                bds.setOffset(total_offset)
                bone_hash = bds.readUInt()
                jointMat = NoeMat44.fromBytes(bds.readBytes(64), 1).toMat43()
                hash_to_mat[bone_hash] = jointMat
                total_offset = bds.getOffset()

    for saved in all_chunk_data_list:
        if saved[0] == 0xB00B:
            block_index = block_list[1]
            block_offset = block_index[0]
            total_offset = block_offset + saved[2]
            size_limit = block_offset + saved[2] + saved[1]
            bds.setOffset(total_offset)
            temp_set = []
            while total_offset < size_limit:
                hash_saver = bds.readUInt()
                temp_set.append(hash_saver)
                total_offset += 4
            bone_maps.append(temp_set)

    for saved in all_chunk_data_list:
        #Retrieves bone hashes
        if saved[0] == 0x8003:
            # Get offset where bone hashes are
            block_index = block_list[1]
            block_offset = block_index[0]
            total_offset = block_offset + saved[2]
            size_limit = block_offset + saved[2] + saved[1]
            # While within size limit, read and save hashes
            while total_offset < size_limit:
                bds.setOffset(total_offset)
                bone_hash_read = bds.readUInt()
                hashList.append(bone_hash_read)
                total_offset += 4

    for saved in all_chunk_data_list:
        #Bone parenting, same order as previous one
        if saved[0] == 0x8009:
            # Get offset where bone parenting info is
            block_index = block_list[1]
            block_offset = block_index[0]
            total_offset = block_offset + saved[2]
            size_limit = block_offset + saved[2] + saved[1]
            while total_offset < size_limit:
                bds.setOffset(total_offset)
                parent = bds.readInt()
                pList.append(parent)
                total_offset += 4

    for saved in all_chunk_data_list:
        if saved[0] == 0x8010:
            # Get offset where bone positions are
            block_index = block_list[1]
            block_offset = block_index[0]
            total_offset = block_offset + saved[2]
            size_limit = block_offset + saved[2] + saved[1]
            count = 0
            while total_offset < size_limit:
                bds.setOffset(total_offset)
                pos = NoeVec3.fromBytes(bds.readBytes(12), 1)
                jointMat = NoeMat43()
                jointMat[3] = pos
                if hashList[count] in hash_to_mat:
                    jointMat = hash_to_mat[hashList[count]]
                elif pList[count] != -1:
                    jointMat*= joint_list[pList[count]].getMatrix()
                joint = NoeBone(count, "joint_" + str(count), jointMat, None, pList[count])
                joint_list.append(joint)
                count += 1
                total_offset = bds.getOffset()



    #Second for loop after data has been read
    mesh_counter = -1
    faces_offset = 0


    vertex_coordinates = []
    uv_map_info = []
    binding_info = []
    bone_assignment = []
    bone_weights = []
    extra_info = []
    faces_data = []


    for saved in all_chunk_data_list:
        # Retrieve vertices data, UV data (not worth using though right now), Bone assignment, and bone weights
        if saved[0] == 0xB006:
            block_index = block_list[-1]
            block_offset = block_index[0]
            total_offset = block_offset + saved[2]
            size_limit = block_offset + saved[2] + saved[1]
            for elements in vertex_attribute_data_list:
                # Sets offset to the right place per sub-chunk!!!
                bds.setOffset(total_offset + int(elements[0]))
                # If collection of UV data
                if elements[1] == 0xFE:
                    # Gets current tuple to look at
                    collect_location = vertex_items_length[mesh_counter]

                    # Saves info
                    uv_maps = bds.readBytes(collect_location[0] * elements[2])
                    uv_map_info.append(uv_maps)
                # Else if collection of binding/unknown
                elif elements[1] == 0xE9:
                    # Gets current tuple to look at
                    collect_location = vertex_items_length[mesh_counter]

                    # Saves info
                    bindings = bds.readBytes(collect_location[0] * elements[2])
                    binding_info.append(bindings)
                # Else if collection of bone assignments
                elif elements[1] == 0xD4:
                    # Gets current tuple to look at
                    collect_location = vertex_items_length[mesh_counter]

                    # Saves info
                    bone_assigners = bds.readBytes(collect_location[0] * elements[2])
                    bone_assignment.append(bone_assigners)
                # Else if collection of bone weights
                elif elements[1] == 0xB0:
                    # Gets current tuple to look at
                    collect_location = vertex_items_length[mesh_counter]

                    # Saves info
                    bone_weighters = bds.readBytes(collect_location[0] * elements[2])
                    bone_weights.append(bone_weighters)

                # Else if its a collection of vertices, put at end to avoid mesh counting issues
                elif elements[1] == 0x0A:
                    if mesh_counter == (len(vertex_items_length) - 1):
                        break
                    # Counts current mesh
                    mesh_counter += 1


                    # Gets current tuple to look at
                    collect_location = vertex_items_length[mesh_counter]

                    # Collects vertices
                    vertices = bds.readBytes(collect_location[0] * elements[2])

                    # Goes to face offset
                    bds.setOffset(faces_offset)

                    # Collects face information
                    face_information = bds.readBytes(collect_location[1] * 2)

                    # Adds to face offset
                    faces_offset += collect_location[1] * 2

                    # Saves information
                    faces_data.append(face_information)
                    vertex_coordinates.append(vertices)
                # Else if not used
                else:
                    # Gets current tuple to look at
                    collect_location = vertex_items_length[mesh_counter]

                    # Saves info
                    extra_unknown = bds.readBytes(collect_location[0] * elements[2])
                    extra_info.append(extra_unknown)


    # Keeps track of the models vs shadows and will only focus on models for now
    model_mesh = 0
    shadow_mesh = 0

    model_bones = 0
    shadow_bones = 0

    # Sorts data into whichever belongs to boxer model and shadow model
    # May allow opportunities later to switch to shadow model but uhhh too lazy right now
    for data in vertex_items_length:
        if data[2] == 0:
            model_mesh += 1
        else:
            shadow_mesh += 1


    # Sets meshes to rpg context
    for items in range(0, model_mesh):
        # Sets reading to Big endian
        rapi.rpgSetOption(noesis.RPGOPT_BIGENDIAN, 1)
        # Sets coordinates
        rapi.rpgBindPositionBuffer(vertex_coordinates[items], noesis.RPGEODATA_FLOAT, 12)
        # Gives each mesh a unique (although not fun to sort through) name
        name = "Mesh" + str(items)
        rapi.rpgSetName(name)
        # Gets the amount of faces and saves them to set faces
        location_saver = vertex_items_length[items]

        bone_mappings = bone_maps[items]
        bone_map_numbers = []

        for bones in bone_maps[items]:
            bonemap_temp = hashList.index(bones)
            bone_map_numbers.append(bonemap_temp)
        rapi.rpgSetBoneMap(bone_map_numbers)
        chosen_assignments = bone_assignment[items]
        chosen_weights = bone_weights[items]
        rapi.rpgBindBoneIndexBuffer(chosen_assignments, noesis.RPGEODATA_BYTE, 4, 1)
        rapi.rpgBindBoneWeightBuffer(chosen_weights, noesis.RPGEODATA_FLOAT, 4, 1)


        rapi.rpgCommitTriangles(faces_data[items], noesis.RPGEODATA_USHORT, location_saver[1], noesis.RPGEO_TRIANGLE_STRIP)


    return joint_list
