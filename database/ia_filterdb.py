import logging
from struct import pack
import re
import base64
from pyrogram.file_id import FileId
from pymongo.errors import DuplicateKeyError
from umongo import Instance, Document, fields
from motor.motor_asyncio import AsyncIOMotorClient
from marshmallow.exceptions import ValidationError
from info import DATABASE_URL, DATABASE_NAME, COLLECTION_NAME

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

client = AsyncIOMotorClient(DATABASE_URL)
db = client[DATABASE_NAME]
instance = Instance.from_db(db)

@instance.register
class Media(Document):
    file_id = fields.StrField(attribute='_id')
    file_name = fields.StrField(required=True)
    file_size = fields.IntField(required=True)
    caption = fields.StrField(allow_none=True)

    class Meta:
        indexes = ('$file_name',)
        collection_name = COLLECTION_NAME

async def save_file(media):
    """Save file in database"""
    
    file_id = unpack_new_file_id(media.file_id)
    file_name = re.sub(r"@\w+|(_|\-|\.|\+)", " ", str(media.file_name))
    
    try:
        file = Media(
            file_id=file_id,
            file_name=file_name,
            file_size=media.file_size,
            caption=media.caption
        )
        await file.commit()
    except ValidationError:
        logger.exception('Error occurred while saving file in database')
        return 'err'
    except DuplicateKeyError:
        logger.warning(f'{file_name} is already saved in database')
        return 'dup'
    except Exception as e:
        logger.exception(f'Some unexpected error occurred: {e}')
        return 'err'
    
    logger.info(f'{file_name} is saved to database')
    return 'suc'

async def get_search_results(query, max_results=10, offset=0, filter=False, lang=None):
    """For given query return (results, next_offset)"""
    
    query = query.strip()
    if not query:
        raw_pattern = '.'
    elif ' ' not in query:
        raw_pattern = r'(\b|[\.\+\-_])' + query + r'(\b|[\.\+\-_])'
    else:
        raw_pattern = query.replace(' ', r'.*[\s\.\+\-_]')
    
    try:
        regex = re.compile(raw_pattern, flags=re.IGNORECASE)
    except re.error:
        return None, None, None
    
    filter = {'file_name': regex}
    cursor = Media.find(filter)

    # Sort by recent
    cursor.sort('$natural', -1)

    if lang:
        lang_files = [file async for file in cursor if lang in file.file_name.lower()]
        files = lang_files[offset:][:max_results]
        total_results = len(lang_files)
        next_offset = offset + max_results
        if next_offset > total_results:
            next_offset = ''
        return files, next_offset, total_results
        
    # Slice files according to offset and max results
    cursor.skip(offset).limit(max_results)
    
    # Get list of files
    files = await cursor.to_list(length=max_results)
    total_results = await Media.count_documents(filter)
    next_offset = offset + max_results
    if next_offset > total_results:
        next_offset = ''
    
    return files, next_offset, total_results

async def delete_files(query, filter=True):
    query = query.strip()
    if filter:
        query = query.replace(' ', r'(\s|\.|\+|\-|_)')
        raw_pattern = r'(\s|_|\-|\.|\+)' + query + r'(\s|_|\-|\.|\+)'
    elif not query:
        raw_pattern = '.'
    else:
        raw_pattern = query.replace(' ', r'.*[\s\.\+\-_]')
    
    try:
        regex = re.compile(raw_pattern, flags=re.IGNORECASE)
    except re.error:
        return None, None
    
    filter = {'file_name': regex}
    total = await Media.count_documents(filter)
    files = Media.find(filter)
    
    return total, files

async def get_file_details(query):
    filter = {'file_id': query}
    cursor = Media.find(filter)
    filedetails = await cursor.to_list(length=1)
    return filedetails

def encode_file_id(s: bytes) -> str:
    r = b""
    n = 0

    for i in s + bytes([22]) + bytes([4]):
        if i == 0:
            n += 1
        else:
            if n:
                r += b"\x00" + bytes([n])
                n = 0
            r += bytes([i])

    return base64.urlsafe_b64encode(r).decode().rstrip("=")

def unpack_new_file_id(new_file_id):
    """Return file_id, file_ref"""
    decoded = FileId.decode(new_file_id)
    file_id = encode_file_id(
        pack(
            "<iiqq",
            int(decoded.file_type),
            decoded.dc_id,
            decoded.media_id,
            decoded.access_hash
        )
    )
    return file_id
