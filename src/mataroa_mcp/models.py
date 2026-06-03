"""Pydantic models for Mataroa API request/response objects."""

from __future__ import annotations

from typing import Optional
from pydantic import BaseModel


class Post(BaseModel):
    title: str
    slug: str
    body: Optional[str] = None
    published_at: Optional[str] = None
    url: Optional[str] = None


class PostCreate(BaseModel):
    title: str
    body: Optional[str] = None
    published_at: Optional[str] = None


class PostUpdate(BaseModel):
    title: Optional[str] = None
    slug: Optional[str] = None
    body: Optional[str] = None
    published_at: Optional[str] = None


class Comment(BaseModel):
    id: int
    post_slug: str
    post_title: str
    post_url: str
    url: str
    created_at: str
    name: str
    email: Optional[str] = None
    body: str
    is_approved: bool
    is_author: bool


class Page(BaseModel):
    title: str
    slug: str
    body: Optional[str] = None
    is_hidden: bool = False
    url: Optional[str] = None


class PageCreate(BaseModel):
    title: str
    slug: str
    body: Optional[str] = None
    is_hidden: bool = False


class PageUpdate(BaseModel):
    title: Optional[str] = None
    slug: Optional[str] = None
    body: Optional[str] = None
    is_hidden: Optional[bool] = None
