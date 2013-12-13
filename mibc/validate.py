
import tests

def validate(obj, **opts):
    test_class_name = repr(obj)+"_Test"
    test_class = getattr(tests, test_class_name)
    validator = test_class(base=obj, cheat_all_tests=True)

    for test_func in validator:
        try:
            validator.setUp()
            test_func()
            validator.tearDown()
        except Exception as e:
            validator.conditions.append( (None, str(e)) )

    return validator.conditions
