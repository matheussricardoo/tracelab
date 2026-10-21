from fastapi import FastAPI, status, HTTPException, Path
from pydantic import BaseModel, Field, ConfigDict

app = FastAPI()


class ExperimentBase(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, allow_inf_nan=False)
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


@app.get(
    "/api/v1/experiments/{experiment_id}",
    response_model=ExperimentResponse,
    status_code=status.HTTP_200_OK,
)
async def get_experiments_by_id(experiment_id: int = Path(gt=0)):
    for experiment in EXPERIMENTS:
        if experiment.id == experiment_id:
            return experiment

    raise HTTPException(status_code=404, detail="ID not found")


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

