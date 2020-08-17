<h1>Mapping from ADLS Gen1 API -> ADLS Gen2 API</h1>
<table style="background:white">
<thead>
<tr>
<th>ADLS Gen1 API</th>
<th>Note for Gen1 API</th>
<th>ADLS Gen2 API</th>
<th>Note for API Mapping</th>
</tr>
</thead>
<tbody>
<tr>
<td>access/exists</td>
<td>To check if file/directory exists.</td>
<td>N/A</td>
<td>User can use Gen2 API: <strong>create_file(if_none_match=&#39;*&#39;)<strong> or </strong>create_directory(if_none_match=&#39;*&#39;)</strong> so that the operation will fail on exist.</td>
</tr>
<tr>
<td>touch</td>
<td>Create empty file</td>
<td><strong>create_file</strong></td>
<td>The API has the same main purpose for Gen1 and Gen2. However Gen2 <strong>create_file</strong> API could accept more parameters along with creation.</td>
</tr>
<tr>
<td>mkdir</td>
<td>Make new directory</td>
<td><strong>create_directory</strong></td>
<td>The API has the same main purpose for Gen1 and Gen2. However Gen2 <strong>create_directory</strong> API could accept more parameters along with creation.</td>
</tr>
<tr>
<td rowspan="2">stat/info</td>
<td rowspan="2">File information for path</td>
<td><strong>get_file_properties</strong></td>
<td rowspan="2">The Gen1 API is split into two separate ones in ADLS Gen2.</td>
</tr>
<tr>
<td><strong>get_directory_properties</strong></td>
</tr>
<tr>
<td rowspan="2">unlink/remove/rm</td>
<td rowspan="2">Remove a file or directory</td>
<td><strong>delete_file</strong></td>
<td rowspan="2">The Gen1 API is split into two separate ones in ADLS Gen2.</td>
</tr>
<tr>
<td><strong>delete_directory</strong></td>
</tr>
<tr>
<td>rmdir</td>
<td>Remove empty directory</td>
<td><strong>delete_directory</strong></td>
<td>Delete directory</td>
</tr>
<tr>
<td>ls/listdir</td>
<td>List all elements under directory specified with path</td>
<td rowspan="2"><strong>get paths</strong></td>
<td><strong>get_paths(recursive=False)</strong> is equal to <strong>ls/listdir</strong></td>
</tr>
<tr>
<td>walk</td>
<td>Walk a path recursively and returns list of files and dirs(if parameter set)</td>
<td><strong>get_paths()</strong> or <strong>get_paths(recursive=True)</strong> is equal to <strong>walk</strong>. <strong>recursive</strong> is <strong>True</strong> by default.</td>
</tr>
<tr>
<td>put</td>
<td>Stream data from local filename to file at path.</td>
<td><strong>append_data</strong> together with <strong>flush_data</strong></td>
<td><strong>append_data</strong> should be followed by <strong>flush_data</strong> , then the data is actually write into the file. <strong>append_data</strong> is just to stage the data, not actually write the data into file.</td>
</tr>
<tr>
<td>cat</td>
<td>Return contents of file</td>
<td rowspan="4"><strong>download_file</strong></td>
<td rowspan="4">Put the expected range parameters in Gen2 API will achieve the same function of the 4 Gen1 APIs.</td>
</tr>
<tr>
<td>head</td>
<td>Return first bytes of file</td>
</tr>
<tr>
<td>tail</td>
<td>Return last bytes of file</td>
</tr>
<tr>
<td><a href="https://docs.microsoft.com/python/API/azure-datalake-store/azure.datalake.store.core.azuredlfilesystem?view=azure-python#read-block-fn--offset--length--delimiter-none-"><strong>read_block</strong></a></td>
<td>Read a block of bytes from an ADL file</td>
</tr>
<tr>
<td>get</td>
<td>Stream data from file at path to local filename</td>
<td><strong>download_file</strong></td>
<td>Passing a <strong>stream</strong> parameter in <strong>download_file</strong> should do the same thing as Gen1 <strong>get</strong> API does</td>
</tr>
<tr>
<td rowspan="2">rename/mv</td>
<td rowspan="2">Move file between locations on ADL</td>
<td><strong>rename_file</strong></td>
<td rowspan="2">Currently ADLS Gen2 only support rename. Move isn&#39;t supported yet.</td>
</tr>
<tr>
<td><strong>rename_directory</strong></td>
</tr>
<tr>
<td>chown</td>
<td>Change owner and/or owning group</td>
<td rowspan="4"><strong>set_access_control</strong></td>
<td rowspan="4">Users can set owner, group, acl etc. using the same API.</td>
</tr>
<tr>
<td>chmod</td>
<td>Change access mode of path</td>
</tr>
<tr>
<td>set_acl</td>
<td>Set the Access Control List (ACL) for a file or folder.</td>
</tr>
<tr>
<td><a href="https://docs.microsoft.com/python/API/azure-datalake-store/azure.datalake.store.core.azuredlfilesystem?view=azure-python#modify-acl-entries-path--acl-spec--recursive-false--number-of-sub-process-none-"><strong>modify_acl_entries</strong></a></td>
<td>Modify existing Access Control List (ACL) entries on a file or folder. If the entry does not exist it is added, otherwise it is updated based on the spec passed in. No entries are removed by this process (unlike set_acl).</td>
</tr>
<tr>
<td>get_acl_status</td>
<td>Gets Access Control List (ACL) entries for the specified file or directory.</td>
<td><strong>get_access_control</strong></td>
<td>The result will include owner, group, acl etc.</td>
</tr>
<tr>
<td>remove_acl_entries</td>
<td>Remove existing, named, Access Control List (ACL) entries on a file or folder.If the entry does not exist already it is ignored. Default entries cannot be removed this way, please use remove_default_acl for that. Unnamed entries cannot be removed in this way, please use remove_acl for that. Note: this is by default not recursive, and applies only to the file or folder specified.</td>
<td rowspan="3">N/A</td>
<td rowspan="3">Probably users can achieve the same purpose by calling set_access_control with related parameters.</td>
</tr>
<tr>
<td><a href="https://docs.microsoft.com/python/API/azure-datalake-store/azure.datalake.store.core.azuredlfilesystem?view=azure-python#remove-acl-path-"><strong>remove_acl</strong></a></td>
<td>Remove the entire, non default, ACL from the file or folder, including unnamed entries. Default entries cannot be removed this way, please use remove_default_acl for that. Note: this is not recursive, and applies only to the file or folder specified.</td>
</tr>
<tr>
<td>remove_default_acl</td>
<td>Remove the entire default ACL from the folder. Default entries do not exist on files, if a file is specified, this operation does nothing. Note: this is not recursive, and applies only to the folder specified.</td>
</tr>
<tr>
<td><a href="https://docs.microsoft.com/python/API/azure-datalake-store/azure.datalake.store.core.azuredlfilesystem?view=azure-python#open-path--mode--rb---blocksize-33554432--delimiter-none-"><strong>open</strong></a></td>
<td>Open a file for reading or writing to.</td>
<td>N/A</td>
<td>There is no open file operation In ADLS Gen2. However users can do operations to the file directly, eg. <strong>append_data, flush_data, download_file</strong></td>
</tr>
<tr>
<td>concat/merge</td>
<td>Concatenate a list of files into one new file</td>
<td>N/A</td>
<td>N/A</td>
</tr>
<tr>
<td>cp</td>
<td>Not implemented. Copy file between locations on ADL</td>
<td>N/A</td>
<td>N/A</td>
</tr>
<tr>
<td>current</td>
<td>Return the most recently created AzureDLFileSystem</td>
<td>N/A</td>
<td>N/A</td>
</tr>
<tr>
<td>df</td>
<td>Resource summary of path. eg. File count, directory count</td>
<td>N/A</td>
<td>get_paths could be a helpful API. But user need to do further processing.</td>
</tr>
<tr>
<td>du</td>
<td>Bytes in keys at path</td>
<td>N/A</td>
<td>get_paths could be a helpful API. But user need to do further processing.</td>
</tr>
<tr>
<td>glob</td>
<td>Find files (not directories) by glob-matching.</td>
<td>N/A</td>
<td>get_paths could be a helpful API. But user need to do further processing.</td>
</tr>
<tr>
<td>set_expiry</td>
<td>Set or remove the expiration time on the specified file. This operation can only be executed against files.</td>
<td>N/A</td>
<td>N/A</td>
</tr>
</tbody>
</table>