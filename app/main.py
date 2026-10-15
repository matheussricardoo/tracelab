from fastapi import FastAPI, status
from pydantic import BaseModel, Field

app = FastAPI()


class ExperimentBase(BaseModel):
    name: str = Field(min_length=1)
    language: str = Field(min_length=1)
    algorithm: str = Field(min_length=1)
    input_size: int = Field(gt=0)
    execution_time_ms: float = Field(ge=0)


class ExperimentCreate(ExperimentBase):
    pass


class ExperimentResponse(ExperimentBase):
    id: int


EXPERIMENTS = []


@app.get("/api/v1/experiments", response_model=list[ExperimentResponse])
async def list_experiments():
    return EXPERIMENTS


@app.post(
    "/api/v1/experiments",
    status_code=status.HTTP_201_CREATED,
    response_model=ExperimentResponse,
)
async def create_experiment(experiment: ExperimentCreate):
    data = experiment.model_dump()
    id = len(EXPERIMENTS) + 1
    new_experiment = ExperimentResponse(id=id, **data)
    EXPERIMENTS.append(new_experiment)
    return new_experiment
