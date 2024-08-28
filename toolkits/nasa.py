from langchain_community.agent_toolkits.nasa.toolkit import NasaToolkit
from langchain_community.utilities.nasa import NasaAPIWrapper

toolkits.append(NasaToolkit.from_nasa_api_wrapper(NasaAPIWrapper()))
