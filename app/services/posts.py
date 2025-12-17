from app.database.db_manager import DBManager
from app.schemes.posts import PostCreate, PostUpdate, PostResponse
from app.exceptions.exceptions import PostNotFound, Forbidden


class PostService:
    def __init__(self, db: DBManager):
        self.db = db

    async def create_post(self, post_data: PostCreate, user_id: int):
        """Create a new post"""
        try:
            post = await self.db.posts.create_post(post_data, user_id)
            await self.db.commit()
            return post
        except Exception as e:
            print(f"[PostService] Error creating post: {e}")
            raise

    async def get_post(self, post_id: int):
        """Get a specific post by ID"""
        try:
            post = await self.db.posts.get_post_by_id(post_id)
            if not post:
                raise PostNotFound()
            
            # Get likes count if available
            try:
                likes_count = await self.db.likes.get_post_likes_count(post_id)
                if hasattr(post, 'likes_count'):
                    post.likes_count = likes_count
            except:
                pass
            
            return post
        except PostNotFound:
            raise
        except Exception as e:
            print(f"[PostService] Error getting post: {e}")
            raise

    async def get_all_posts(self, skip: int = 0, limit: int = 10):
        """Get all posts with pagination"""
        try:
            posts = await self.db.posts.get_all_posts(skip, limit)
            if not posts:
                return []
            
            # Try to add likes count if method available
            result = []
            for post in posts:
                try:
                    likes_count = await self.db.likes.get_post_likes_count(post.id)
                    if hasattr(post, 'likes_count'):
                        post.likes_count = likes_count
                except:
                    pass
                result.append(post)
            
            return result
        except Exception as e:
            print(f"[PostService] Error getting all posts: {e}")
            raise

    async def get_user_posts(self, user_id: int, skip: int = 0, limit: int = 10):
        """Get all posts by a specific user"""
        try:
            posts = await self.db.posts.get_user_posts(user_id, skip, limit)
            if not posts:
                return []
            
            # Try to add likes count if method available
            result = []
            for post in posts:
                try:
                    likes_count = await self.db.likes.get_post_likes_count(post.id)
                    if hasattr(post, 'likes_count'):
                        post.likes_count = likes_count
                except:
                    pass
                result.append(post)
            
            return result
        except Exception as e:
            print(f"[PostService] Error getting user posts: {e}")
            raise

    async def update_post(self, post_id: int, post_data: PostUpdate, current_user_id: int):
        """Update a post"""
        try:
            post = await self.db.posts.get_post_by_id(post_id)
            if not post:
                raise PostNotFound()
            if post.user_id != current_user_id:
                raise Forbidden()
            
            updated_post = await self.db.posts.update_post(post_id, post_data)
            await self.db.commit()
            return updated_post
        except (PostNotFound, Forbidden):
            raise
        except Exception as e:
            print(f"[PostService] Error updating post: {e}")
            raise

    async def delete_post(self, post_id: int, current_user_id: int) -> bool:
        """Delete a post"""
        try:
            post = await self.db.posts.get_post_by_id(post_id)
            if not post:
                raise PostNotFound()
            if post.user_id != current_user_id:
                raise Forbidden()
            
            result = await self.db.posts.delete_post(post_id)
            await self.db.commit()
            return result
        except (PostNotFound, Forbidden):
            raise
        except Exception as e:
            print(f"[PostService] Error deleting post: {e}")
            raise
