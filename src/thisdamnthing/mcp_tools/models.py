"""Shared typed MCP inputs, outputs and response envelopes."""
from pydantic import BaseModel, ConfigDict, Field, model_validator
from typing import Annotated, Generic, Literal, TypeVar


class Model(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)


class ReadInput(Model):
    budget_bytes: int = Field(default=32768, ge=1024, le=131072)


class ProjectAddInput(ReadInput):
    path: str = Field(min_length=1, max_length=400)


class ProjectCreateInput(ReadInput):
    relative_folder: str = Field(min_length=1, max_length=400)


class ProjectRegistered(Model):
    id: str
    result: Literal['registered', 'existing']


class CaptureRequestInput(ReadInput):
    request_id: str = Field(pattern='^[a-f0-9]{64}$')


class CaptureListInput(ReadInput):
    limit: int = Field(default=20, ge=1, le=50)
    cursor: str | None = Field(default=None, max_length=512)
    status: Literal['requested', 'captured', 'skipped', 'all'] = 'requested'


class CaptureRequest(Model):
    id: str
    status: Literal['requested', 'captured', 'skipped']
    created: str
    completed: str | None
    provenance: dict
    revision: str


class CapturePage(Model):
    items: list[CaptureRequest]
    next_cursor: str | None
    inventory_revision: str


class CaptureSummary(Model):
    title: str = Field(min_length=1, max_length=160)
    kind: Literal['fact', 'decision', 'question', 'inference']
    body: str = Field(min_length=1, max_length=3000)
    sources: list[str] = Field(min_length=1, max_length=8)
    links: list[str] = Field(default_factory=lambda: ['index'], min_length=1, max_length=8)
    project: str | None = None


class CaptureSummaryPayload(Model):
    action: Literal['summary']
    summary: CaptureSummary


class ProjectInspectInput(ReadInput):
    id: str = Field(pattern='^[a-f0-9]{64}$')


class ProjectProposeInput(ProjectInspectInput):
    summary: CaptureSummary


class ProjectProposed(Model):
    id: str
    status: Literal['pending', 'approved', 'rejected']
    result: Literal['saved', 'existing']


class ProjectDocument(Model):
    source: str
    text: str | None = None
    truncated: bool = False
    omitted: str | None = None


class InspectedRegistration(Model):
    id: str
    path: str
    created: str
    status: Literal['active', 'archived'] = 'active'


class ProjectInspection(Model):
    project: InspectedRegistration
    brain_link: str | None
    top_level: list[str]
    inventory_truncated: bool
    documents: list[ProjectDocument]
    notice: str


class ScratchpadSummary(CaptureSummary):
    tags: list[str] = Field(min_length=1, max_length=8)


class KnowledgeSaveInput(ReadInput):
    summary: CaptureSummary
    user_instruction: str = Field(min_length=1, max_length=500)


class NoteSaveInput(KnowledgeSaveInput):
    summary: ScratchpadSummary


class SavedNote(Model):
    id: str
    status: Literal['approved', 'scratchpad']
    result: Literal['saved', 'existing']


class CandidateDecision(Model):
    action: Literal['approve', 'reject']


class CandidateEdit(Model):
    action: Literal['edit']
    summary: CaptureSummary


class CandidateStatusInput(ReadInput):
    id: str = Field(pattern='^[a-f0-9]{64}$')


class CandidateReviewInput(CandidateStatusInput):
    expected_sha256: str = Field(pattern='^[a-f0-9]{64}$')
    user_instruction: str = Field(min_length=1, max_length=500)
    decision: Annotated[CandidateDecision | CandidateEdit, Field(discriminator='action')]


class CandidateReviewed(Model):
    id: str
    status: Literal['pending', 'approved', 'rejected']


class CandidateStatus(Model):
    id: str
    status: Literal['pending', 'approved', 'rejected']
    path: str
    revision: str
    markdown: str
    approval_destination: str
    pending_cleanup: bool = False


class CaptureSkipPayload(Model):
    action: Literal['skip']


class CaptureSubmitInput(CaptureRequestInput):
    payload: Annotated[CaptureSummaryPayload | CaptureSkipPayload, Field(discriminator='action')]


class CaptureSubmitted(Model):
    id: str
    status: Literal['captured', 'skipped']


class CaptureSuppressInput(ReadInput):
    token: str = Field(pattern='^[a-f0-9]{128}$')


class CaptureSuppressed(Model):
    result: Literal['suppressed'] = 'suppressed'


class ReminderChangeInput(ReadInput):
    id: str = Field(pattern='^[a-f0-9]{64}$')
    reminder_revision: int = Field(ge=1, le=9223372036854775806)
    user_instruction: str = Field(min_length=1, max_length=500)


class ReminderChanged(Model):
    id: str
    reminder_revision: int
    status: Literal['pending', 'done', 'cancelled']


class ReminderCreateInput(ReadInput):
    title: str = Field(min_length=1, max_length=160)
    body: str = Field(min_length=1, max_length=1500)
    due_at: str = Field(min_length=1, max_length=100)
    timezone: str = Field(min_length=1, max_length=100)
    user_instruction: str = Field(min_length=1, max_length=500)


class ReminderCreated(ReminderChanged):
    result: Literal['saved', 'existing']


class ReminderSnoozeFields(Model):
    due_at: str = Field(min_length=1, max_length=100)
    timezone: str | None = Field(default=None, min_length=1, max_length=100)

    @model_validator(mode='after')
    def supplied_fields(self):
        values = self.model_dump(exclude_unset=True)
        if not values or any(value is None for value in values.values()):
            raise ValueError('Supply at least one non-null changed field')
        return self


class ReminderEditFields(ReminderSnoozeFields):
    due_at: str | None = Field(default=None, min_length=1, max_length=100)
    title: str | None = Field(default=None, min_length=1, max_length=160)
    body: str | None = Field(default=None, min_length=1, max_length=1500)


class ReminderEditInput(ReminderChangeInput):
    changes: ReminderEditFields


class ReminderSnoozeInput(ReminderChangeInput):
    changes: ReminderSnoozeFields


class ReminderSettings(Model):
    timezone: str | None
    chat: bool
    schedule: str | None


class ReminderConfigureFields(Model):
    timezone: str | None = Field(default=None, min_length=1, max_length=100)
    chat: bool | None = None
    schedule: str | None = Field(default=None, min_length=1, max_length=500)

    @model_validator(mode='after')
    def supplied_fields(self):
        values = self.model_dump(exclude_unset=True)
        if not values or any(value is None for key, value in values.items() if key != 'schedule'):
            raise ValueError('Supply changed fields; only schedule may be null to clear it')
        return self


class ReminderConfigureInput(ReadInput):
    changes: ReminderConfigureFields
    user_instruction: str = Field(min_length=1, max_length=500)


class ReminderConfigured(Model):
    result: Literal['configured'] = 'configured'


class ReminderClaimInput(ReadInput):
    channel: Literal['manual', 'chat', 'scheduled']
    limit: int = Field(default=10, ge=1, le=20)


class ReminderDelivery(Model):
    id: str
    reminder_revision: int
    title: str
    body: str
    due_at: str
    timezone: str
    token: str
    channel: Literal['manual', 'chat', 'scheduled']
    expires_at: str


class ReminderClaims(Model):
    items: list[ReminderDelivery]


class ReminderAckInput(ReadInput):
    id: str = Field(pattern='^[a-f0-9]{64}$')
    token: str = Field(pattern='^[a-f0-9]{64}$')


class ReminderAcknowledged(Model):
    id: str
    result: Literal['notified', 'already-notified']


class SearchInput(ReadInput):
    query: str = Field(min_length=1, max_length=300)
    limit: int = Field(default=20, ge=1, le=50)
    depth: int = Field(default=1, ge=0, le=3)


class ProviderSearchInput(SearchInput):
    providers: list[Annotated[str, Field(pattern=r"^[a-z][a-z0-9.-]{0,79}$")]] = Field(min_length=1, max_length=8)

    @model_validator(mode="after")
    def distinct_providers(self):
        if len(set(self.providers)) != len(self.providers):
            raise ValueError("Select distinct providers")
        return self


class NoteInput(ReadInput):
    reference: str = Field(min_length=1, max_length=512)


class ListInput(ReadInput):
    limit: int = Field(default=20, ge=1, le=50)
    cursor: str | None = Field(default=None, max_length=512)


class DiscoveryInput(ListInput):
    query: str = Field(min_length=1, max_length=300)


class StackSummary(Model):
    id: str
    version: str
    origin: dict


class StackPage(Model):
    items: list[StackSummary]
    next_cursor: str | None
    inventory_revision: str


class ProviderSummary(Model):
    id: str
    version: str
    capabilities: list[dict]
    compatibility: dict
    trusted: bool


class ProviderPage(Model):
    items: list[ProviderSummary]
    next_cursor: str | None
    inventory_revision: str


class RelatedInput(ListInput):
    id: str = Field(pattern='^[a-f0-9]{64}$')


class WorkSearchInput(ReadInput):
    query: str = Field(min_length=1, max_length=300)
    limit: int = Field(default=20, ge=1, le=50)


class WorkMatch(Model):
    path: str
    uri: str
    status: Literal['working-file'] = 'working-file'
    content_truncated: bool
    text_readable: bool


class WorkResults(Model):
    items: list[WorkMatch]
    scan_truncated: bool
    content_truncated: bool
    limit_reached: bool


class WorkRead(Model):
    path: str
    uri: str
    status: Literal['working-file'] = 'working-file'
    revision: str
    content: str
    content_truncated: bool


class CandidateInput(ListInput):
    status: Literal['pending', 'rejected', 'all'] = 'pending'


class ReminderInput(ListInput):
    status: Literal['pending', 'done', 'cancelled', 'all'] = 'pending'


class ReminderSummary(Model):
    id: str
    path: str
    uri: str
    revision: str
    reminder_revision: int
    status: Literal['pending', 'done', 'cancelled']
    title: str
    due_at: str
    timezone: str
    notified_at: str | None
    claimed: bool


class ReminderRead(ReminderSummary):
    markdown: str


class ReminderPage(Model):
    items: list[ReminderSummary]
    next_cursor: str | None = None
    inventory_revision: str


class StoredSummary(Model):
    id: str
    path: str
    uri: str
    revision: str
    status: Literal['pending', 'rejected', 'scratchpad']
    title: str
    tags: list[str] = Field(default_factory=list)


class StoredNote(StoredSummary):
    # Complete original proposal, including provenance, sources and review history.
    markdown: str


class StoredPage(Model):
    items: list[StoredSummary]
    next_cursor: str | None = None
    inventory_revision: str


class RelatedNote(StoredSummary):
    shared_tags: list[str]


class RelatedPage(Model):
    items: list[RelatedNote]
    next_cursor: str | None = None
    inventory_revision: str


class ProjectSummary(Model):
    id: str
    uri: str
    path: str
    created: str
    status: Literal['active', 'archived']
    availability: Literal['available', 'missing or moved', 'archived']
    revision: str


class ProjectPage(Model):
    items: list[ProjectSummary]
    next_cursor: str | None = None
    inventory_revision: str


class Registration(Model):
    path: str
    uri: str
    revision: str
    markdown: str


class ProjectRead(Model):
    project: ProjectSummary
    registration: Registration | None = None
    registration_status: Literal['available', 'missing']


class WorkspaceStatus(Model):
    workspace_key: str
    observed_at: str
    pending_candidates: int | None
    incomplete_captures: int
    projects_total: int
    projects_available: int
    projects_missing: int
    projects_archived: int
    due_reminders: int | None
    recovery_markers: list[str]


class DocumentSummary(Model):
    id: str
    path: str
    uri: str
    owner: str
    revision: str
    description: str | None = None


class DocumentRead(DocumentSummary):
    markdown: str


class DocumentPage(Model):
    items: list[DocumentSummary]
    next_cursor: str | None = None
    inventory_revision: str


class Policy(Model):
    sha256: str
    markdown: str | None


class Context(Model):
    workspace_key: str
    profile: Literal['read-only', 'everyday'] = 'read-only'
    policy: Policy
    filing_conventions: str | None
    tools: list[str]


class Evidence(Model):
    path: str
    uri: str
    revision: str
    status: Literal['approved'] = 'approved'
    title: str
    content: str


class SearchResults(Model):
    items: list[Evidence]
    limit: int
    depth: int
    # Core search stops at the requested limit, so completeness is not inferred.
    limit_reached: bool


class Coverage(Model):
    truncated: bool = False
    omissions: list[str] = Field(default_factory=list)


class Error(Model):
    code: str
    message: str
    retry: Literal['safe', 'reread', 'inspect_outcome'] = 'reread'


Data = TypeVar('Data')


class Result(Model, Generic[Data]):
    api_version: Literal[1] = 1
    ok: bool = True
    data: Data | None = None
    coverage: Coverage = Field(default_factory=Coverage)
    warnings: list[str] = Field(default_factory=list)
    error: Error | None = None
