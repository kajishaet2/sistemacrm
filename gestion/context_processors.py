from .models import ConfiguracionEmpresa


def empresa_context(request):
    return {'empresa_config': ConfiguracionEmpresa.get_config()}
